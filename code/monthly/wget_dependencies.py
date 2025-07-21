import os
import sys
import pytz
import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from os.path import join
from util import handle_retry


hcdp_api_token = os.environ.get('HCDP_API_TOKEN')
local_dep_dir = os.environ.get('DEPENDENCY_DIR')

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
    url = f"https://api.hcdp.ikewai.org/raster?period=month&date={date}&extent=statewide&{dataset2params(dataset)}"
    print(url)
    found = False
    res = requests.get(url, headers = {'Authorization': f'Bearer {hcdp_api_token}'}, timeout = 5)
    #if file was not found ignore the error and return false, otherwise raise error to be handled by retry
    if res.status_code != 404:
        #raise error if request has a failure code
        res.raise_for_status()
        with open(outf, 'wb') as f:
            f.write(res.content)
        found = True
    return found


#Get rainfall for the last 60 months
months_back = 60
for dataset, fname_prefix in datasets:
    for i in range(months_back):
        date = targ_dt - relativedelta(months=i)
        outf = join(local_dep_dir, f"{fname_prefix}_{date.year}_{date.month:02d}.tif")
        date_s = date.strftime('%Y-%m')
        #if a map was not found any longer term SPI is invalid, stop retrieving maps
        if not handle_retry(get_raster, (date_s, dataset, outf)):
            print(f"Rainfall map for {date_s} was not found. Stopping dependency retrieval at map {i}...")
            break
