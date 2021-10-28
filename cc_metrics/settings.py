
from environs import Env
from . import metrics, api

env = Env()
env.read_env()

BLOB_STORAGE_CONNECTION_STRING = env.str("BLOB_STORAGE_CONNECTION_STRING")
GENERAL_CACHE_CONTAINER_NAME = env.str("GENERAL_CACHE_CONTAINER_NAME")

DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")
DB_USER = env.str("DB_USER")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_NAME = env.str("DB_NAME")

GED_API_URL = env.str("GED_API_URL", "http://ged")

PREDS_API_URL = env.str("PREDS_API_URL", "http://api")
USERS_API_URL = env.str("USERS_API_URL", PREDS_API_URL)
COUNTRY_API_URL = env.str("COUNTRY_API_URL", PREDS_API_URL)

SCHEDULER_URL = env.str("SCHEDULER_API_URL", "http://scheduler")

"""
These metrics will be computed when doing a pass.
"""
METRICS = [
        (metrics.actuals,           api.ActualsType.Points),
        (metrics.correct,           api.ActualsType.Points),
        (metrics.discrepancy,       api.ActualsType.Points),
        (metrics.conflict_coverage, api.ActualsType.Buffered),
        (metrics.square_km_area,    api.ActualsType.Points),
    ]
