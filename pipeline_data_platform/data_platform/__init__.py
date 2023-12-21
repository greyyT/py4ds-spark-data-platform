from dagster import Definitions, load_assets_from_modules

from data_platform.assets import raw_movies, raw_reviews, staging_reviews


review_assets = load_assets_from_modules([raw_reviews, staging_reviews])
movie_assets = load_assets_from_modules([raw_movies])

defs = Definitions(
    assets=[*review_assets, *movie_assets],
)
