from dagster import MetadataValue, asset, OpExecutionContext
import gdown, os

from . import constants


@asset(group_name="raw_files")
def pretrained_comments(context: OpExecutionContext):
    file_id = constants.PRETRAINED_COMMENTS_FILE_ID
    dest_dir = constants.PRETRAINED_COMMENTS_FILE_PATH

    # Google drive download link
    url = f"https://drive.google.com/uc?id={file_id}"

    # Create the data folder if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    context.log.info("Downloading...")
    gdown.download(url, f"{dest_dir}", quiet=True)

    context.log.info("Done!")
    context.add_output_metadata({"File path": MetadataValue.path(dest_dir)})
