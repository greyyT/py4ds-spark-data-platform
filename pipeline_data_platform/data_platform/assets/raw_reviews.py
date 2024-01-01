from dagster import asset, MetadataValue, OpExecutionContext
import gdown, os, csv
import pandas as pd

from . import constants
from data_platform.partitions import batch_partition
from data_platform.resources.scraper import IMDBScraper, logger as scraper_logger


@asset(
    group_name="raw_files",
    description="Download pretrained reviews from Google Drive.",
)
def pretrained_reviews(context: OpExecutionContext):
    """
    Download the pretrained reviews dataset from Google Drive.
    """
    file_id = constants.PRETRAINED_REVIEWS_FILE_ID
    dest_dir = constants.PRETRAINED_REVIEWS_FILE_PATH

    # Google drive download link
    url = f"https://drive.google.com/uc?id={file_id}"

    # Create the data folder if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    context.log.info("Downloading...")
    gdown.download(url, f"{dest_dir}", quiet=True)

    context.log.info("Done!")
    context.add_output_metadata({"File path": MetadataValue.path(dest_dir)})


@asset(
    group_name="raw_files",
    description="User's reviews about a movie",
    partitions_def=batch_partition,
    deps=["movies"],
    compute_kind="Python",
)
def reviews(
    context: OpExecutionContext,
    IMDB_scraper: IMDBScraper,
):
    """
    Scrape user's reviews about a movie from IMDB.com
    """
    current_batch = context.asset_partition_key_for_output().split("-")
    start_num, end_num = int(current_batch[0]), int(current_batch[1])

    # Retrieve list of movies' id from
    movies_df = pd.read_csv(f"{constants.MOVIES_FILE_PATH}/{start_num}-{end_num}.csv")
    links = movies_df["link"]
    movie_ids = [link.strip().split("/")[-2] for link in links]

    # Create folder directory if not exists
    dest_dir = constants.REVIEWS_FILE_PATH
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Create file if not exists
    if not os.path.exists(f"{dest_dir}/{start_num}-{end_num}.csv"):
        with open(f"{dest_dir}/{start_num}-{end_num}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["movie_id", "review", "is_positive"])

    # Start scraping
    scraper = IMDB_scraper
    scraper_logger.info("Starting IMDB scraper")

    movies_reviews_list = []
    for index, movie_id in enumerate(movie_ids):
        context.log.info(
            f"<======== Scraping movie {index+1} of {len(movie_ids)} movies ========>"
        )
        reviews_list = scraper.scrape_comments_by_id(movie_id)
        movies_reviews_list.append(reviews_list)
        context.log.info("Finished scraping reviews from this movie!")

    context.log.info("Saving to csv...")
    for reviews_list in movies_reviews_list:
        with open(f"{dest_dir}/{start_num}-{end_num}.csv", "a", newline="\n") as f:
            writer = csv.writer(f)
            writer.writerows(reviews_list)
