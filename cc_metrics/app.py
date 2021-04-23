
from fastapi import FastAPI,Response
from . import schema,api,config

app = FastAPI()

ged_api = api.Ged(config.config("GED_API_URL"))
preds_api = api.Predictions(config.config("PREDS_API_URL"))

@app.get("/abs/{user}/{gwno}/{year}/{quarter}")
def abs_report(user:int, gwno:int, year:int, quarter:int):
    return schema.QuarterlyReport

@app.get("/rel/{user}/{gwno}/{shift}")
def rel_report(user:int,gwno:int,shift:int): 
    return schema.QuarterlyReport

@app.get("/sum/{user}")
def summary(user:int):
    return schema.Summary

@app.get("/sum/{user}/{gwno}")
def year_summary(user:int):
    return schema.YearlySummary

@app.get("/touch/{gwno}/{year}/{quarter}")
async def touch(gwno:int, year:int, quarter:int):
    """
    Checks if it is possible to compute metrics for the quarter,
    and does so if it is possible.
    """
    return Response(status_code=204)
