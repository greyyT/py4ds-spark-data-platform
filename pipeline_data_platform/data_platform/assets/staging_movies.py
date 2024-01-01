from dagster import (
    AssetOut,
    asset,
    multi_asset,
    OpExecutionContext,
)
from dagster_pyspark import PySparkResource

from data_platform.assets import constants


@multi_asset(
    group_name="staging",
    outs={"train_movies": AssetOut(), "test_movies": AssetOut()},
    deps=["movies"],
    compute_kind="PySpark",
)
def train_test_movies(context: OpExecutionContext):
    pass


@asset(
    group_name="staging",
    description="Clean ans transform raw movies",
    deps=["movies", "thumbnails"],
    compute_kind="PySpark",
)
def cleaned_movies(context: OpExecutionContext, spark: PySparkResource):
    sc = spark.spark_context
    context.log.info(f"Spark session: {spark}")
    context.log.info(f"Spark context: {sc}")

    context.log.info(f"RDD: {sc.paralellize([1, 2, 3, 4]).collect()}")
