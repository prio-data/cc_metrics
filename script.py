import sys
import logging
from cc_metrics.app import preds_api,users_api,country_api,scheduler_api,ged_api
from cc_metrics.batch import add_null_predictions ,compute_metrics

logging.basicConfig(level=logging.INFO)

shift = int(sys.argv[1])

add_null_predictions(preds_api,country_api,scheduler_api,users_api,shift)
compute_metrics(ged_api,preds_api,scheduler_api,country_api,shift)
