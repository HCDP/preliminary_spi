#SET UP FROM PRODUCTION BASE IMAGE
FROM ghcr.io/hcdp/task-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/preliminary_spi"
LABEL org.opencontainers.image.description="Base Image for Standard Precipitation Index workflows."

RUN pip install --upgrade pip
RUN python3 -m pip install rasterio
RUN python3 -m pip install numpy
RUN python3 -m pip install tqdm
RUN python3 -m pip install pandas
RUN python3 -m pip install scipy
RUN python3 -m pip install joblib
RUN python3 -m pip install pytz
RUN python3 -m pip install python-dateutil
RUN python3 -m pip install https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/workflow_data/preliminary/spi/dependencies/climate_indices-0.1.0-py3-none-any.whl

RUN mkdir -p /workspace/code
RUN mkdir -p /workspace/dependencies
RUN mkdir -p /workspace/envs
RUN mkdir -p /sync

RUN wget https://raw.githubusercontent.com/ikewai/data-uploader/main/upload.py -O /sync/upload.py

ADD /tools /sync