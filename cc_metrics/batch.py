"""
Batch tasks
"""
from contextlib import closing
from config import METRICS
from . import api,models,db

def compute_metrics(ged_api:Ged, preds_api:Predictions,year:int, quarter:int):
    with closing(db.Session()) as sess:
        predictions = preds_api.get(year = year, quarter = quarter)["features"] #TODO year-quarter api not implemented
        predictions.sort(key = lambda pred: pred["properties"]["countries_id"])

        
        actuals = dict()
        country = None 
        for prediction in predictions:
            if prediction["properties"]["country_id"] != country:
                for actuals_type in api.ActualsType.Points,api.ActualsType.Buffered:
                    actuals[actuals_type] = ged_api(actuals_type,country,year,quarter)

            for metric,actuals_type in METRICS:
                metric = models.Metric.compute(sess,metric,prediction,actuals[actuals_type])
                sess.add(metric)

            country = prediction["properties"]["country_id"]

        sess.commit()
