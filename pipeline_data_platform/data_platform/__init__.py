from dagster import Definitions, EnvVar, load_assets_from_modules

from data_platform.assets import (
    raw_movies,
    raw_reviews,
    raw_thumbnails,
    staging_reviews,
    staging_movies,
    models,
)
from data_platform.resources.scraper import IMDBScraper
from data_platform.resources.mysql import MySQLResource
from dagster_pyspark import PySparkResource


review_assets = load_assets_from_modules([raw_reviews, staging_reviews])
movie_assets = load_assets_from_modules([raw_movies, staging_movies])
thumbnail_assets = load_assets_from_modules([raw_thumbnails])
model_assets = load_assets_from_modules([models])

defs = Definitions(
    assets=[*review_assets, *movie_assets, *thumbnail_assets, *model_assets],
    resources={
        "IMDB_scraper": IMDBScraper(),
        "mysql_conn": MySQLResource(
            db_host=EnvVar("MYSQL_HOST"),
            username=EnvVar("MYSQL_USER"),
            password=EnvVar("MYSQL_PASSWORD"),
            database=EnvVar("MYSQL_DATABASE"),
        ),
        "spark": PySparkResource(
            spark_config={
                "spark.app.name": "pipeline",
                "spark.master": "spark://192.168.194.64:7077",
                "spark.driver.memory": "4g",
                "spark.executor.memory": "4g",
                "spark.pyspark.python": "/usr/bin/python3",
                "spark.pyspark.driver.python": "/usr/bin/python3",
            }
        ),
    },
)
