import logging
from cc_metrics.app import preds_api,users_api,country_api,scheduler_api,ged_api
from cc_metrics.batch import add_null_predictions ,compute_metrics

logging.basicConfig(level=logging.INFO)

add_null_predictions(preds_api,country_api,scheduler_api,users_api,-1)
compute_metrics(ged_api,preds_api,scheduler_api,country_api,0)
