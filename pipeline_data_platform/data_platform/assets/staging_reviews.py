from dagster import AssetOut, multi_asset, OpExecutionContext, Output, MetadataValue

from data_platform.assets import constants


@multi_asset(
    group_name="staging",
    outs={"train_reviews": AssetOut(), "test_reviews": AssetOut()},
    deps=["reviews", "pretrained_reviews"],
    compute_kind="PySpark",
)
def train_test_reviews(context: OpExecutionContext):
    pass
