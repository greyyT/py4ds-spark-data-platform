from dagster import asset, OpExecutionContext
import pandas as pd, os, csv

from . import constants
from data_platform.partitions import batch_partition
from data_platform.resources.scraper import IMDBScraper, logger as scraper_logger


@asset(
    group_name="raw_files",
    description="Movie's thumbnail",
    partitions_def=batch_partition,
    deps=["movies"],
    compute_kind="Python",
)
def thumbnails(
    context: OpExecutionContext,
    IMDB_scraper: IMDBScraper,
):
    """
    Scrape thumbnail of movies from IMDB.com

    Parameters: None

    Returns:
    - Output[pd.DataFrame]: The pandas.DataFrame contains {id, src, alt}
      of movies in a batch_partition.
    """
    current_batch = context.asset_partition_key_for_output().split("-")
    start_num, end_num = int(current_batch[0]), int(current_batch[1])

    # Retrieve list of movies' id
    movies_df = pd.read_csv(f"{constants.MOVIES_FILE_PATH}/{start_num}-{end_num}.csv")
    links = movies_df["link"]
    movie_ids = [link.strip().split("/")[-2] for link in links]

    # Create folder directory if not exists
    dest_dir = constants.THUMBNAILS_FILE_PATH
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Create file if not exists
    if not os.path.exists(f"{dest_dir}/{start_num}-{end_num}.csv"):
        with open(f"{dest_dir}/{start_num}-{end_num}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["movie_id", "src", "alt"])

    # Start scraping
    scraper = IMDB_scraper
    scraper_logger.debug("Starting IMDB scraper")

    thumbnails_list = []
    for index, movie_id in enumerate(movie_ids):
        context.log.info(
            f"<======== Scraping movie {index+1} of {len(movie_ids)} movies ========>"
        )
        thumbnail: list = scraper.scrape_thumbnail_by_id(movie_id)
        if len(thumbnail) == 0:
            continue
        thumbnails_list.append(thumbnail)
        context.log.debug(f"Result: {thumbnail}")
        context.log.info("Finished scraping reviews from this movie!")

    context.log.info("Saving to csv...")
    with open(f"{dest_dir}/{start_num}-{end_num}.csv", "a", newline="\n") as f:
        writer = csv.writer(f)
        writer.writerows(thumbnails_list)
