
from fastapi import FastAPI,Response,BackgroundTasks
from . import schema, api, config, metrics, batch

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

@app.get("/touch/{year}/{quarter}")
async def touch(year:int, quarter:int,background_tasks: BackgroundTasks):
    """
    Checks if it is possible to compute metrics for the quarter,
    and does so if it is possible.
    """
    background_tasks.add_task(batch.compute_metrics, year=year, quarter=quarter, ged_api = ged_api, preds_api = preds_api)
    return Response(status_code=204)

