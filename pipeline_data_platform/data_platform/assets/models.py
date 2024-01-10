from dagster import asset, OpExecutionContext, MetadataValue
from dagster_pyspark import PySparkResource
from pyspark.sql.functions import col
from pyspark.sql.types import ArrayType, StringType, FloatType, IntegerType
import pyspark.sql.functions as F
import re, math

from data_platform.assets import constants


@asset(group_name="modelling", deps=["cleaned_movies"], compute_kind="PySpark")
def tf_idf(context: OpExecutionContext, pyspark: PySparkResource):
    """
    Calculate tf_idf model
    """
    spark = pyspark.spark_session
    sc = pyspark.spark_context
    context.log.debug(f"Spark session: {spark}")
    context.log.debug(f"Spark context: {sc}")

    # Read input dataframe (cleaned_movies)
    context.log.info("Read input")
    input_dir = constants.STAGING_MOVIES_FILE_PATH + ".parquet"
    df = spark.read.parquet(input_dir, inferSchema=True)
    df = df.drop(
        "movie_id",
        "score",
        "duration",
        "director_name",
        "actor_1_name",
        "actor_2_name",
        "actor_3_name",
        "num_reviews",
        "num_critics",
        "num_votes",
        "metascore",
        "language",
        "global_gross",
        "year",
        "link",
        "src",
        "alt",
    )
    df = df.filter((col("overview").isNotNull()) & (col("overview") != ""))

    context.log.info("Model, output = tfidf")
    total_docs = df.count()

    def tokenize(text):
        return re.findall("\\w+", text.lower())

    # Register tokenizer as a udf
    tokenize_udf = F.udf(tokenize, ArrayType(StringType()))
    # Tokenize all the text
    data = df.select(["title", tokenize_udf("overview").alias("overview")])
    # Make 1 separate row for each token
    data_tokens = data.withColumn("token", F.explode("overview"))

    # Calculate term frequency
    tf = data_tokens.groupBy("title", "token").agg(F.count("overview").alias("tf"))
    # Calculate document frequency
    df = data_tokens.groupBy("token").agg(F.countDistinct("title").alias("df"))

    def inverse_doc_frequency(doc_frequency):
        return math.log((total_docs + 1) * 1.0 / (doc_frequency + 1))

    # Register inverse document frequency as a udf
    inverse_doc_frequency_udf = F.udf(inverse_doc_frequency, FloatType())
    # Calculate the inverse document frequency
    idf = df.withColumn("idf", inverse_doc_frequency_udf("df"))
    # Calculate tfidf
    tfidf = tf.join(idf, "token").withColumn("tfidf", F.col("tf") * F.col("idf"))

    # Save into parquet
    context.log.info("Save into parquet")
    dest_dir = constants.MODEL_TFIDF_PATH + ".parquet"
    tfidf.write.mode("overwrite").parquet(dest_dir)

    asset_metadata = {
        "File path": MetadataValue.path(dest_dir),
        "Count": MetadataValue.int(tfidf.count()),
        "Columns": MetadataValue.text(str(tfidf.columns)),
    }
    context.add_output_metadata(asset_metadata)
