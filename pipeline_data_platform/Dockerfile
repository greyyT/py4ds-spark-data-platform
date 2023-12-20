FROM python:3.8.10-slim

# Checkout and install dagster libraries needed to run the gRPC server
# exposing your repository to dagster-webserver and dagster-daemon, and to load the DagsterInstance

# Setup java version
ARG openjdk_version="17"

# Install sqlite3 for storing logs
RUN apt-get update \
  && apt-get install sqlite3 net-tools iputils-ping -y \
  && apt-get install --yes curl "openjdk-${openjdk_version}-jre-headless" ca-certificates-java procps \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install spark
RUN curl -O https://dlcdn.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz \
  && tar zxvf spark-3.5.0-bin-hadoop3.tgz \
  && mv spark-3.5.0-bin-hadoop3/ /usr/local/spark \
  && rm -rf spark-3.5.0-bin-hadoop3.tgz

# Install necessary jars
RUN curl -O https://repo1.maven.org/maven2/software/amazon/awssdk/s3/2.18.41/s3-2.18.41.jar \
  && curl -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk/1.12.367/aws-java-sdk-1.12.367.jar \
  && curl -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.1026/aws-java-sdk-bundle-1.11.1026.jar \
  && curl -O https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.2.0/delta-core_2.12-2.2.0.jar \
  && curl -O https://repo1.maven.org/maven2/io/delta/delta-storage/2.2.0/delta-storage-2.2.0.jar \
  && curl -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.2/hadoop-aws-3.3.2.jar \
  && mv s3-2.18.41.jar /usr/local/spark/jars \
  && mv aws-java-sdk-1.12.367.jar /usr/local/spark/jars \
  && mv aws-java-sdk-bundle-1.11.1026.jar /usr/local/spark/jars \
  && mv delta-core_2.12-2.2.0.jar /usr/local/spark/jars \
  && mv delta-storage-2.2.0.jar /usr/local/spark/jars \
  && mv hadoop-aws-3.3.2.jar /usr/local/spark/jars

# Install python dependencies
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
