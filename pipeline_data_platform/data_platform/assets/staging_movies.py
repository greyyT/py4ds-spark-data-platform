from dagster import (
    asset,
    multi_asset,
    AssetOut,
    OpExecutionContext,
    MetadataValue,
)
from dagster_pyspark import PySparkResource
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import split, when, col, regexp_replace, udf

from data_platform.assets import constants


@asset(
    group_name="staging",
    description="Clean ans transform raw movies",
    deps=["movies", "thumbnails"],
    compute_kind="PySpark",
)
def cleaned_movies(
    context: OpExecutionContext,
    pyspark: PySparkResource,
):
    """
    Output handled by:
    - Local storage, at constants.STAGING_MOVIES_FILE_PATH
    - MySQL, at imdb.movies
    """
    spark = pyspark.spark_session
    sc = pyspark.spark_context
    context.log.debug(f"Spark session: {spark}")
    context.log.debug(f"Spark context: {sc}")

    movies_df = spark.read.csv(
        constants.MOVIES_FILE_PATH, header=True, inferSchema=True
    )

    # Convert duration to minutes
    context.log.debug("Convert duration to minutes")
    movies_df = movies_df.withColumn(
        "duration", regexp_replace("duration", "h", ":")
    ).withColumn("duration", regexp_replace("duration", "m", ""))
    # Rows with NULL will turn to 0:00
    movies_df = movies_df.withColumn(
        "duration", when(col("duration") == "", "0:00").otherwise(col("duration"))
    )
    # Add 0: to the duration if it's just minutes
    movies_df = movies_df.withColumn(
        "duration",
        when(col("duration").contains(":"), col("duration")).otherwise(
            "0:" + col("duration")
        ),
    )
    # Remove any spaces in the duration
    movies_df = movies_df.withColumn("duration", regexp_replace("duration", " ", ""))

    # Define the UDF function
    def convert_to_number_udf(x):
        key_decimals = {"K": 1000, "M": 1000000, "B": 1000000000}
        if isinstance(x, str):
            x = x.replace(",", "")
            if x[-1] in key_decimals.keys():
                change = float(x[:-1]) * key_decimals[x[-1]]
                return int(change)
            else:
                return int(x)
        else:
            return x

    # Register the UDF
    convert_to_number_spark_udf = udf(convert_to_number_udf, IntegerType())
    # Convert number of reviewed users, number of reviewed critics, number of votes
    context.log.debug(
        "Convert number of reviewed users, number of reviewed critics, number of votes"
    )
    movies_df = movies_df.withColumn(
        "num_reviews", convert_to_number_spark_udf(movies_df["num_reviews"])
    )
    movies_df = movies_df.withColumn(
        "num_critics", convert_to_number_spark_udf(movies_df["num_critics"])
    )
    movies_df = movies_df.withColumn(
        "num_votes", convert_to_number_spark_udf(movies_df["num_votes"])
    )

    # Drop budget column
    context.log.debug("Drop budget")
    movies_df = movies_df.drop("budget")

    # Convert global gross to integer
    context.log.debug("Convert global gross to integer")
    movies_df = movies_df.withColumn(
        "global_gross", regexp_replace("global_gross", "[^0-9]", "")
    ).withColumn("global_gross", col("global_gross").cast("integer"))

    # Convert year to integer
    context.log.debug("Convert year to integer")
    movies_df = movies_df.withColumn("year", col("year").cast("integer"))

    # Create column movie_id
    context.log.debug("Create column movie_id")
    movies_df = movies_df.withColumn("movie_id", split(col("link"), "/").getItem(4))
    movies_df = movies_df.filter(col("movie_id").isNotNull())

    # Read thumbnails
    thumbnails_df = spark.read.csv(
        constants.THUMBNAILS_FILE_PATH, header=True, inferSchema=True
    )

    # Join 2 dataframes
    context.log.debug("Join movies_df and thumbnails_df")
    joined_df = movies_df.join(
        thumbnails_df, movies_df.movie_id == thumbnails_df.movie_id, how="left"
    )

    # Drop 1 column movie_id
    joined_df = joined_df.drop(thumbnails_df.movie_id)

    # Drop duplicates
    context.log.debug("Drop duplicates")
    joined_df = joined_df.dropDuplicates()

    # Save into parquet
    context.log.info("Save into parquet")
    dest_dir = constants.STAGING_MOVIES_FILE_PATH + ".parquet"
    joined_df.write.mode("overwrite").parquet(dest_dir)

    # Write into MySQL
    context.log.info("Save into mysql")
    joined_df.write.format("jdbc").options(
        url=f"jdbc:mysql://172.21.0.3/imdb",
        driver="com.mysql.jdbc.Driver",
        dbtable="movies",
        user="root",
        password="password",
    ).mode("append").save()

    asset_metadata = {
        "File path": MetadataValue.path(dest_dir),
        "Count": MetadataValue.int(joined_df.count()),
        "Columns": MetadataValue.text(str(joined_df.columns)),
    }
    context.add_output_metadata(asset_metadata)
