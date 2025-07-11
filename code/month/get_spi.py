import rasterio
import numpy as np
import os
from climate_indices import compute, indices, utils
from joblib import Parallel, delayed
from tqdm import tqdm
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import sys
import pytz
from dateutil import parser

local_dep_dir = os.environ.get('DEPENDENCY_DIR')

def load_param_tif(folder, prefix, month):
    fname = f"{prefix}_{month:02d}.tif"
    fpath = os.path.join(folder, fname)

    with rasterio.open(fpath) as src:
        arr = src.read(1).astype(np.float32)
        nodata = src.nodata
        arr = np.where(arr == nodata, np.nan, arr)
    return arr

def get_params(month_date, spi_scale): 
    end_date = datetime(month_date.year, month_date.month, 1)
    months_needed = [
        ((end_date - relativedelta(months=i)).year,
        (end_date - relativedelta(months=i)).month)
        for i in reversed(range(spi_scale))
    ]
    rainfall_stack = []

    for year, month in months_needed:
        fname = f"rainfall_{year}_{month:02d}.tif"
        fpath = os.path.join(local_dep_dir, fname)

        with rasterio.open(fpath) as src:
            arr = src.read(1).astype(np.float32)
            nodata = src.nodata
            arr = np.where(arr == nodata, np.nan, arr)
            rainfall_stack.append(arr)

    alphas = load_param_tif(local_dep_dir, f"SPI{spi_scale}_alpha", month_date.month)
    betas = load_param_tif(local_dep_dir, f"SPI{spi_scale}_beta", month_date.month)
    prob_zero = load_param_tif(local_dep_dir, f"SPI{spi_scale}_prob_zero", month_date.month)

    lat_len, lon_len = alphas.shape
    spi_result = np.full((lat_len, lon_len), np.nan, dtype=np.float32)
    rainfall_stack = np.stack(rainfall_stack, axis=-1)
    return rainfall_stack, alphas, betas, prob_zero, spi_result

def compute_spi(lat_idx, lon_idx, values, spi_scale, alphas, betas, prob_zeros, month_date):
    if (np.ma.is_masked(values) and values.mask.all()) or np.all(np.isnan(values)):
        return lat_idx, lon_idx, None

    try:
        alpha = alphas[lat_idx, lon_idx].copy()
        beta = betas[lat_idx, lon_idx].copy()
        prob_zero = prob_zeros[lat_idx, lon_idx].copy()

        if np.isnan(alpha).all() or np.isnan(beta).all():
            print(f"NaN alpha/beta at lat={lat_idx}, lon={lon_idx}")
            return lat_idx, lon_idx, None

        spi_vals = indices.spi(
            values,
            scale=spi_scale,
            distribution=indices.Distribution.gamma,
            data_start_year=month_date.year,
            calibration_year_initial=1991,
            calibration_year_final=2020,
            periodicity=compute.Periodicity.monthly,
            fitting_params={
                "alpha": alpha,
                "beta": beta,  
                "prob_zero": prob_zero,
            },
        )
        return lat_idx, lon_idx, spi_vals
    except Exception as e:
        print(f"Error at lat={lat_idx}, lon={lon_idx}: {e}")
        return lat_idx, lon_idx, None
    
def save_tif(spi_array, month_date, spi_scale):
    with rasterio.open(local_dep_dir + f"rainfall_{month_date.year}_{month_date.month:02d}.tif") as ref:
        meta = ref.meta.copy()

        with rasterio.open(f"SPI{spi_scale}_{month_date.year}_{month_date.month:02d}.tif", "w", **meta) as dst:
            dst.write(spi_array, 1)

def run_spi_pipeline(month_date, spi_scale):
    rainfall_stack, alphas, betas, prob_zero, _ = get_params(month_date, spi_scale)

    n_lats, n_lons, _ = rainfall_stack.shape
    spi_array = np.full((n_lats, n_lons), np.nan, dtype=np.float32)

    jobs = [
        (lat, lon)
        for lat in tqdm(range(n_lats), desc="Building job list (lat)")
        for lon in range(n_lons)
    ]

    def worker(lat_idx, lon_idx):
        values = np.asarray(rainfall_stack[lat_idx, lon_idx])
        _, _, spi_val = compute_spi(lat_idx, lon_idx, values, spi_scale, alphas, betas, prob_zero, month_date)
        return lat_idx, lon_idx, spi_val

    results = Parallel(n_jobs=-1, backend="loky")(
        delayed(worker)(lat, lon) for lat, lon in tqdm(jobs, desc="Computing SPI")
    )

    for lat_idx, lon_idx, spi_val in results:
        if spi_val is not None and not np.isnan(spi_val[-1]):
            spi_array[lat_idx, lon_idx] = spi_val[-1]
    save_tif(spi_array, month_date, spi_scale)

if __name__=="__main__":
    scale = int(sys.argv[1])
    if len(sys.argv) > 2:
        input_date = sys.argv[2]
        month_date = parser.parse(input_date)
    else:
        hst = pytz.timezone('HST')
        today = datetime.today().astimezone(hst)
        prev = today - timedelta(months=1)
        month_date = datetime(prev.year,prev.month,1)
    run_spi_pipeline(month_date, scale)