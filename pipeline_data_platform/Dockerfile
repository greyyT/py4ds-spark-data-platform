FROM python:3.8.10-slim

# Checkout and install dagster libraries needed to run the gRPC server
# exposing your repository to dagster-webserver and dagster-daemon, and to load the DagsterInstance

# Install sqlite3 for storing logs
RUN apt-get update \
  && apt-get install sqlite3 -y \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/dagster/app/pipeline_data_platform
COPY setup.py .
COPY pyproject.toml .

RUN pip install -e "."

# Add repository code
COPY . /opt/dagster/app/pipeline_data_platform
RUN mkdir data/ models/

# Run dagster gRPC server on port 4000
EXPOSE 4000

# CMD allows this to be overridden from run launchers or executors that want
# to run other commands against your repository
CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-m", "data_platform"]
