from dagster import StaticPartitionsDefinition
from ..assets import constants


num_batches = constants.NUM_BATCHES

batch_partition = StaticPartitionsDefinition(
    [f"{x*50-49}-{x*50}" for x in range(1, num_batches + 1)]
)
