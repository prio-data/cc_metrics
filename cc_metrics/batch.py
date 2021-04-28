"""
Batch tasks
"""
import logging
from contextlib import closing
from . import api,models,db,config

logger = logging.getLogger(__name__)

class CantCompute(Exception):
    pass

span_dates = lambda span: (span["start"],span["end"])

def compute_metrics(
        ged_api:api.Ged,
        preds_api:api.Predictions,
        scheduler_api:api.Scheduler,
        shift:int):
    preds_span,ged_span = (scheduler_api.get(b+shift) for b in range(-2,0))

    ged_start,ged_end = span_dates(ged_span)
    try:
        ged_api.get_points(100,ged_end.year,ged_end.month)
    except api.DoesNotExist:
        logger.info("No ged data for {ged_end} yet.")
        
    preds_start,preds_end = span_dates(preds_span)
    countries = preds_api.get_countries(start_date=preds_start,end_date=preds_end)
    with closing(db.Session()) as sess:
        for c in countries:
            gwno = c["gwno"] 
            if (sess
                    .query(models.Metric)
                    .join(models.shapes)
                    .filter(models.shapes.c.country_id == gwno)
                    .first() is not None
                    ):
                logger.info("There is already a metric for %s",gwno)
                continue
            preds = preds_api.get(country = gwno) 
            for month in range(ged_start.month,ged_end.month+1):
                actuals = {}

                actuals[api.ActualsType.Points] = ged_api.get_points(
                        gwno,year=ged_end.year,month=month)

                actuals[api.ActualsType.Buffered] = ged_api.get_buffered(
                        gwno,year=ged_end.year,month=month)

                for prediction in preds["features"]:
                    for metric,required_type in config.METRICS:
                        exists = (sess
                                .query(models.Metric)
                                .get((int(prediction["id"]),metric.__name__))
                            ) is not None

                        if not exists:
                            logger.info("Computing metric %s for %s",
                                    metric.__name__,
                                    prediction["id"]
                                )
                            metric = models.Metric.compute(
                                    sess,metric,prediction,actuals[required_type])
                            sess.add(metric)
                        else:
                            logger.info("Metric %s for %s exists",
                                    metric.__name__,
                                    prediction["id"]
                                )
            logger.info("Adding metrics for %s",gwno)
            sess.commit()
