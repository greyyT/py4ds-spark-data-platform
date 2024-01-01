from contextlib import contextmanager
from dagster import ConfigurableResource, InitResourceContext
from sqlalchemy import Connection, Engine, create_engine
from pydantic import PrivateAttr
from pyspark.sql import DataFrame
import logging


# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s] %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class MySQLResource(ConfigurableResource):
    db_host: str
    username: str
    password: str
    database: str
    port: int = 3306

    _engine: Engine = PrivateAttr()
    _connection: Connection = PrivateAttr()

    @contextmanager
    def yield_for_execution(self, context: InitResourceContext):
        conn_metadata = f"mysql://{self.username}:{self.password}@{self.db_host}:{self.port}/{self.database}"
        try:
            self._engine = create_engine(url=conn_metadata)
            with self._engine.connect() as conn:
                self._connection = conn
                logger.info(f"Connected to MySQL: {self._connection}")
                yield self
        except Exception as e:
            logger.exception(f"Error while connecting to MySQL: {e}")

    def teardown_after_execution(self, context: InitResourceContext) -> None:
        self._connection.close()
        return super().teardown_after_execution(context)
