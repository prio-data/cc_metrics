import logging
from fastapi import FastAPI,Response,BackgroundTasks
from . import schema, api, config, metrics, batch

logging.basicConfig(level=logging.INFO)

app = FastAPI()

ged_api = api.Ged(config.config("GED_API_URL"))
preds_api = api.Predictions(config.config("PREDS_API_URL"))
scheduler_api = api.Scheduler(config.config("SCHEDULER_URL"))

@app.get("/compute/")
def compute_metrics(shift:int,background_tasks:BackgroundTasks):
    background_tasks.add_task(batch.compute_metrics,
            ged_api = ged_api, preds_api = preds_api, scheduler_api = scheduler_api,
            shift = shift
        )
