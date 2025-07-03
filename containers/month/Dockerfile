FROM ghcr.io/hcdp/task-preliminary-spi-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/preliminary_spi"
LABEL org.opencontainers.image.description="Monthly Standard Precipitation Index"

ADD /envs/month/prod.env /workspace/envs

WORKDIR /workspace/dependencies
RUN wget -nv https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/workflow_data/preliminary/spi/dependencies/monthly_dependencies.tar.gz
RUN tar -xf monthly_dependencies.tar.gz
RUN rm monthly_dependencies.tar.gz

ADD /code/month /workspace/code
# Get the container's upload config as specified in the code repo.
ADD /containers/month/configs/upload.json /sync/config.json
# Add the task wrapper script.
ADD /containers/month/task.sh /workspace/task.sh

WORKDIR /workspace
# This container is intended to run the task wrapper at launch, unless otherwise specified at run-time.
CMD [ "/bin/bash", "task.sh" ]
