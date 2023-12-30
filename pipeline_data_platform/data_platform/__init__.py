from dagster import Definitions, load_assets_from_modules

from data_platform.assets import (
    raw_movies,
    raw_reviews,
    staging_reviews,
    staging_movies,
    models,
)
from data_platform.resources.scraper import IMDBScraper


review_assets = load_assets_from_modules([raw_reviews, staging_reviews])
movie_assets = load_assets_from_modules([raw_movies, staging_movies])
model_assets = load_assets_from_modules([models])

defs = Definitions(
    assets=[*review_assets, *movie_assets, *model_assets],
    resources={"IMDB_scraper": IMDBScraper},
)
