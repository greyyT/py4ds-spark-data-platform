from dagster import Definitions, load_assets_from_modules

from data_platform.assets import raw_movies, raw_comments


comment_assets = load_assets_from_modules([raw_comments])
movie_assets = load_assets_from_modules([raw_movies])

defs = Definitions(
    assets=[*comment_assets, *movie_assets],
)
