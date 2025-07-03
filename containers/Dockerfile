#SET UP FROM PRODUCTION BASE IMAGE
FROM ghcr.io/hcdp/task-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/preliminary_spi"
LABEL org.opencontainers.image.description="Base Image for Standard Precipitation Index workflows."


RUN mkdir -p /workspace/code
RUN mkdir -p /workspace/dependencies
RUN mkdir -p /workspace/envs
RUN mkdir -p /sync

RUN wget https://raw.githubusercontent.com/ikewai/data-uploader/main/upload.py -O /sync/upload.py

ADD /tools /sync