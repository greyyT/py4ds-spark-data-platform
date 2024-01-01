from dagster import ConfigurableResource, InitResourceContext
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from contextlib import contextmanager
from pydantic import PrivateAttr
import pandas as pd
import logging


# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s] %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class SparkApp:
    pass


@contextmanager
def get_spark_session(master_url: str, app_name: str):
    spark_conf = SparkConf()
    spark_conf.setAppName(app_name)
    spark_conf.setMaster(master_url)
    spark_conf.set("spark.executor.memory", "4g")
    spark_conf.set("spark.driver.memory", "4g")
    spark_conf.set("spark.pyspark.python", "/usr/bin/python3")
    spark_conf.set("spark.pyspark.driver.python", "/usr/bin/python3")

    spark = None
    try:
        spark = SparkSession.builder.config(conf=spark_conf).getOrCreate()
        yield spark
    except Exception as e:
        logger.exception(f"Error while getting spark app: {e}")
    finally:
        if spark:
            spark.stop()


class SparkResource(ConfigurableResource):
    master_url: str
