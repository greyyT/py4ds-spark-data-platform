from dagster import asset, OpExecutionContext, MetadataValue, Output
import pandas as pd, os

from . import constants
from data_platform.partitions import batch_partition
from data_platform.resources.scraper import IMDBScraper, logger as scraper_logger


@asset(
    group_name="raw_files",
    description="Scrape raw movie metadata from IMDB.com",
    partitions_def=batch_partition,
    compute_kind="Python",
)
def movies(
    context: OpExecutionContext,
    IMDB_scraper: IMDBScraper,
) -> Output[pd.DataFrame]:
    """
    Scrape raw movie metadata from IMDB.com

    Parameters: None

    Returns:
    - Output[pd.DataFrame]: The pandas.DataFrame contains metadata of movies
    in a batch_partition.
    """
    current_batch = context.asset_partition_key_for_output().split("-")
    start_num, end_num = int(current_batch[0]), int(current_batch[1])
    dest_dir = constants.MOVIES_FILE_PATH

    # Create folder directory if not exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Start scraping
    scraper = IMDB_scraper
    scraper_logger.info("Starting IMDB scraper")

    movies_list = scraper.scrape_movies_by_single_batch(start_num, end_num)

    cols = [
        "score",
        "title",
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
        "budget",
        "global_gross",
        "year",
        "overview",
        "link",
    ]

    # Create dataframe from the list above
    movies_df = pd.DataFrame(movies_list, columns=cols)

    # Save to file
    movies_df.to_csv(f"{dest_dir}/{start_num}-{end_num}.csv", index=False, header=True)

    asset_metadata = {
        "File path": MetadataValue.path(dest_dir),
        "Count": MetadataValue.int(len(movies_df)),
        "Columns": MetadataValue.text(str(movies_df.columns)),
    }

    context.add_output_metadata(asset_metadata)

    return Output(movies_df, metadata=asset_metadata)
