
from enum import Enum
from environs import Env
from fitin import views_config
from . import metrics,api

env = Env()
env.read_env()

config = views_config(env.str("KEYVAULT_URL"))

"""
These metrics will be computed when doing a pass
"""
METRICS = [
        (metrics.actuals,           api.ActualsType.Points),
        (metrics.correct,           api.ActualsType.Points),
        (metrics.discrepancy,       api.ActualsType.Points),
        (metrics.conflict_coverage, api.ActualsType.Buffered),
    ]
