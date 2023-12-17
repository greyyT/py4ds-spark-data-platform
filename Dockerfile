# Dagster libraries to run both dagster-webserver and the dagster-daemon. Does not
# need to have access to any pipeline code.

FROM python:3.8.10-slim

# Install sqlite3 for storing logs
RUN apt-get update \
  && apt-get install sqlite3 -y \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
  dagster==1.4.17 \
  dagster-graphql==1.4.17 \
  dagster-webserver==1.4.17 \
  dagster-docker==0.20.17 \
  pendulum==2.1.2

# Set $DAGSTER_HOME and copy dagster instance and workspace YAML there
ENV DAGSTER_HOME=/opt/dagster/dagster_home/

RUN mkdir -p $DAGSTER_HOME

COPY dagster_home/dagster.yaml $DAGSTER_HOME
COPY dagster_home/workspace.yaml $DAGSTER_HOME

WORKDIR $DAGSTER_HOME
