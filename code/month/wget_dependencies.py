import os
import sys
import subprocess
import pytz
import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from util import handle_retry
from os.path import join
print(os.getcwd())


# ***CHANGE THIS TO YOUR LOCAL DEPENDENCY DIRECTORY***
hcdp_api_token = os.environ.get('HCDP_API_TOKEN')
local_dep_dir = os.environ.get('DEPENDENCY_DIR')
remote_baseurl = "https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/workflow_data/preliminary/spi/dependencies/monthly/"


datasets = [({"datatype": "rainfall", "production": "new"}, "rainfall")]

targ_dt = None

if len(sys.argv) > 1:
    target_date = sys.argv[1]
    targ_dt = pd.to_datetime(target_date)
else:
    hst = pytz.timezone('HST')
    today = datetime.now(hst)
    targ_dt = today - relativedelta(months=1)



def dataset2params(dataset):
    return "&".join("=".join(item) for item in dataset.items())

def get_raster(date, dataset, outf):
    date_s = date.strftime('%Y-%m')
    url = f"https://api.hcdp.ikewai.org/raster?period=month&date={date_s}&extent=statewide&{dataset2params(dataset)}&returnEmptyNotFound=False"
    print(url)
    found = False
    try:
        req = requests.get(url, headers = {'Authorization': f'Bearer {hcdp_api_token}'}, timeout = 5)
        req.raise_for_status()
        with open(outf, 'wb') as f:
            f.write(req.content)
        found = True
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] Request failed: {e}")
    return found


#Get rainfall for the last 60 months
months_back = 60
for dataset, fname_prefix in datasets:
    for i in range(months_back):
        print(i)
        date = targ_dt - relativedelta(months=i)
        outf = join(local_dep_dir, f"{fname_prefix}_{date.year}_{date.month:02d}.tif")
        get_raster(date, dataset, outf)
