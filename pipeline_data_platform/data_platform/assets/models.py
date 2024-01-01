from dagster import AssetOut, asset, OpExecutionContext, Output, MetadataValue
from pyspark.sql import SparkSession

from data_platform.assets import constants


@asset(group_name="modelling", deps=["train_movies", "test_movies"])
def tf_idf(context: OpExecutionContext):
    pass
