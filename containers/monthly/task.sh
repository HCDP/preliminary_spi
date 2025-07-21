#!/bin/bash
echo "[task.sh] [1/5] Starting Execution."
export TZ="HST"
echo "It is currently $(date)."
if [ $CUSTOM_DATE ]; then
    export CUSTOM_DATE=$(date -d "$CUSTOM_DATE" +"%Y-%m-01")
    export CUSTOM_DATE=$(date -d "$CUSTOM_DATE +1 month -1 day" --iso-8601)
    echo "An aggregation date was provided by the environment. Setting to last day of provided month."
else
    export CUSTOM_DATE=$(date -d "-$(date +%d) days" --iso-8601)
    echo "No aggregation date was provided by the environment. Defaulting to last month."
fi

echo "Aggregation date is: " $CUSTOM_DATE
source /workspace/envs/prod.env

echo "[task.sh] [2/5] Get dependencies."
python3 /workspace/code/wget_dependencies.py $CUSTOM_DATE

echo "[task.sh] [3/5] GET SPI-X."
python3 /workspace/code/get_spi.py 1 $CUSTOM_DATE
python3 /workspace/code/get_spi.py 3 $CUSTOM_DATE
python3 /workspace/code/get_spi.py 6 $CUSTOM_DATE
python3 /workspace/code/get_spi.py 9 $CUSTOM_DATE
python3 /workspace/code/get_spi.py 12 $CUSTOM_DATE
python3 /workspace/code/get_spi.py 24 $CUSTOM_DATE
python3 /workspace/code/get_spi.py 36 $CUSTOM_DATE
python3 /workspace/code/get_spi.py 48 $CUSTOM_DATE
python3 /workspace/code/get_spi.py 60 $CUSTOM_DATE

cd /sync
echo "[task.sh] [4/5] Uploading data."
python3 inject_upload_config.py config.json $CUSTOM_DATE

echo "[task.sh] [5/5] Uploading data."
python3 upload.py

echo "[task.sh] All done!"