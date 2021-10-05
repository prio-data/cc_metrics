import sys
import logging
from cc_metrics.app import preds_api,users_api,country_api,scheduler_api,ged_api
from cc_metrics.batch import add_null_predictions ,compute_metrics

logging.basicConfig(level=logging.INFO)

try:
    shift = int(sys.argv[1])
except (IndexError, ValueError):
    print("Usage: python compute_metrics.py SHIFT")
    sys.exit(1)

# Adds null predictions for previous month
add_null_predictions(preds_api,country_api,scheduler_api,users_api,shift)

# Adds evaluation metrics for previous month 
compute_metrics(ged_api,preds_api,scheduler_api,country_api,shift)
