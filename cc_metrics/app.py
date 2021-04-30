import logging
from fastapi import FastAPI,Response,BackgroundTasks
from contextlib import closing
from . import schema, api, config, metrics, batch, models, db

logging.basicConfig(level=logging.INFO)

app = FastAPI()

ged_api = api.Ged(config.config("GED_API_URL"))
preds_api = api.Predictions(config.config("PREDS_API_URL"))
users_api = api.Users(config.config("USERS_API_URL"))
country_api = api.Country(config.config("COUNTRY_API_URL"))

scheduler_api = api.Scheduler(config.config("SCHEDULER_URL"))

@app.get("/{user:int}/available/")
def available(user:int):
    """
    Returns a list of available time-periods (shifts)
    """
    pass

@app.get("/{user:int}/{shift:int}/countries")
def time_countries(user:int,shift:int):
    """
    Returns a list of available countries for a time-period
    """
    pass

@app.get("/{user:int}/summary")
def summary(user:int):
    """
    Returns an overall summary of metrics for the user
    """
    pass

@app.get("/{user:int}/{shift:int}/countries/{gwno:int}/")
def data(user:int,shift:int,gwno:int):
    """
    Returns data associated with an evaluated time-period-country
    """
    pass

