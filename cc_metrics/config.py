
from environs import Env

import fitin
from azure_blob_storage_cache import BlobCache

from . import metrics,api

env = Env()
env.read_env()

config = fitin.seek_config([
            fitin.views_config(env.str("KEYVAULT_URL")),
            fitin.dict_resolver({
                    "GED_API_URL":"http://ged",
                    "PREDS_API_URL":"http://api",
                })
        ])

"""
These metrics will be computed when doing a pass
"""
METRICS = [
        (metrics.actuals,           api.ActualsType.Points),
        (metrics.correct,           api.ActualsType.Points),
        (metrics.discrepancy,       api.ActualsType.Points),
        (metrics.conflict_coverage, api.ActualsType.Buffered),
    ]

general_cache = BlobCache(config("STORAGE_CONNECTION_STRING"),config("GENERAL_CACHE_CONTAINER"))
