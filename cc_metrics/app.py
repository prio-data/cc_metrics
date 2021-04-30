from typing import Optional
import logging
from fastapi import FastAPI,Response,BackgroundTasks
from contextlib import closing
from . import schema, api, config, metrics, batch, models, db, crud

logging.basicConfig(level=logging.INFO)

app = FastAPI()

ged_api = api.Ged(config.config("GED_API_URL"))
preds_api = api.Predictions(config.config("PREDS_API_URL"))
users_api = api.Users(config.config("USERS_API_URL"))
country_api = api.Country(config.config("COUNTRY_API_URL"))
scheduler_api = api.Scheduler(config.config("SCHEDULER_URL"))

def get_summary(session,user,country=None,shift=None):
    if shift:
        start_date,end_date = scheduler_api.get_start_end(shift)
    else:
        start_date,end_date = None,None 
    return crud.summary(session,user,start_date,end_date,country)

@app.get("/{user:int}/")
def summary(user:int,shift:Optional[int]=None):
    """
    Returns an overall summary of metrics for the user
    """
    with closing(db.Session()) as sess:
        return get_summary(sess,user=user)

@app.get("/{user:int}/countries")
def time_countries(user:int,shift:Optional[int]=None):
    """
    Returns a list of available countries for a time-period for the user
    """
    if shift:
        start_date,end_date = scheduler_api.get_start_end(shift)
    else:
        start_date,end_date = None,None
    with closing(db.Session()) as sess:
        countries = crud.metric_countries_in_span(sess,user,start_date,end_date)
    return countries

@app.get("/{user:int}/countries/{gwno:int}/")
def data(user:int,gwno:int,shift:Optional[int]=None):
    """
    Returns a summary for a user for the time-period for the country
    """
    with closing(db.Session()) as sess:
        return get_summary(sess,user=user,country=gwno,shift=shift)
