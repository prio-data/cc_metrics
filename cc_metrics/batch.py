"""
Batch tasks
"""
from contextlib import closing
from datetime import date
import logging
from functools import reduce
from sqlalchemy.orm import Session
from shapely.geometry import shape,mapping

from . import api,models,config,db,spatial

logger = logging.getLogger(__name__)

class CantCompute(Exception):
    pass

class NoAnswer(Exception):
    pass

class IntegrityError(Exception):
    pass

span_dates = lambda span: (span["start"],span["end"])

empty_feature = lambda geometry: {"type":"Feature","geometry":geometry,"properties":{}}

def feature_collection_union(a,b):
    a["features"] += b["features"]
    return a

def preds_null_prediction(predictions,country):
    country_shape = shape(country["geometry"]).buffer(0)
    if len(predictions["features"]) > 0:
        pred_shapes = [shape(feature["geometry"]).buffer(0) for feature in predictions["features"]]
        preds_union = reduce(lambda x,y: x.union(y), pred_shapes)
        preds_union = preds_union.buffer(0)
        return mapping(country_shape.difference(preds_union))
    else:
        return mapping(country_shape)

def has_null_pred(session,user,country):
    return (session
            .query(models.Shape)
            .filter(models.Shape.country_id == country)
            .filter(models.Shape.author_id == user)
            .filter(models.Shape.null_prediction.is_(True))
            .first()
        ) is not None


def add_user_null_predictions(
        preds_api: api.Predictions,
        country_api: api.Country,
        user_api: api.Users,
        author: int,
        start_date: date,
        end_date: date
        ):
    """
    Idempotent function that adds null predictions for a users'
    contributions between two dates, if the user has added shapes or
    made a null-prediction.
    """
    with closing(db.Session()) as session:
        profile = user_api.get_detail(author,start_date=start_date,end_date=end_date)

        nullpredictions = []

        for country in {shp["country_id"] for shp in profile["participation"]["shapes"]}:
            if has_null_pred(session,author,country):
                logger.info("Null prediction exists for user %s shape participation in %s",
                        author,country
                        )
                continue

            logger.info("Making null prediction for user %s shape participation in %s",
                    author,country
                    )
            predictions = preds_api.get(
                    country=country,
                    user=author,
                    start_date=start_date,
                    end_date=end_date)

            logger.info("Retrieved %s predictions for %s - %s - %s - %s",
                    len(predictions["features"]),
                    country,
                    author,
                    start_date,
                    end_date)

            country_feature = country_api.get(country)

            shape = models.Shape(
                    author_id = author,
                    country_id = country,
                    values = {"intensity":-1,"confidence":100},
                    shape = empty_feature(preds_null_prediction(predictions,country_feature)),
                    null_prediction = True,
                    date = end_date
                    )

            nullpredictions.append(shape)

        for country in {shp["country_id"] for shp in profile["participation"]["nonanswers"]}:
            if has_null_pred(session,author,country):
                logger.info("Null prediction exists for user %s shape participation in %s",
                        author,country
                        )
                continue

            logger.info("Making null prediction for user %s nonanswer participation in %s",
                    author,country
                    )

            country_feature = country_api.get(
                    country
                )

            shape = models.Shape(
                    author_id = author,
                    country_id = country, 
                    values = {"intensity":-1,"confidence":100},
                    shape = empty_feature(country_feature["geometry"]),
                    null_prediction = True,
                    date = end_date
                    )
            nullpredictions.append(shape)
        
        for np in nullpredictions:
            session.add(np)

        session.commit()

def add_null_predictions(
        preds_api: api.Predictions,
        country_api: api.Country,
        scheduler_api: api.Scheduler,
        user_api: api.Users,
        shift:int=0):

    try:
        assert shift <= 0
    except AssertionError as ae:
        raise IntegrityError("Null predictions can only be added to past pred. periods") from ae
    
    span = scheduler_api.get(-1+shift)

    for user in user_api.get_list():
        logger.info("Adding null-predictions for user %s",user["id"])
        add_user_null_predictions(preds_api,country_api,user_api,user["id"],span["start"],span["end"])

def compute_metrics(
        ged_api:api.Ged,
        preds_api:api.Predictions,
        scheduler_api:api.Scheduler,
        country_api: api.Country,
        shift:int=0):
    preds_span,ged_span = (scheduler_api.get(b+shift) for b in range(-2,0))

    ged_start,ged_end = span_dates(ged_span)
    try:
        ged_api.get_points(100,ged_end.year,ged_end.month)
    except api.DoesNotExist:
        logger.info("No ged data for {ged_end} yet.")
        
    preds_start,preds_end = span_dates(preds_span)
    print(preds_end)

    countries = country_api.get_list(
            only_active=True,
            with_contributions=True,
            start_date=preds_start,
            end_date=preds_end
        )

    with closing(db.Session()) as session:
        for c in countries:
            gwno = c["gwno"] 

            """
            Remove this?
            if (session
                    .query(models.Metric)
                    .join(models.shapes)
                    .filter(models.shapes.c.country_id == gwno)
                    .first() is not None
                    ):
                logger.info("There is already a metric for %s",gwno)
                continue
                """

            preds = preds_api.get(country = gwno,start_date=preds_start,end_date=preds_end) 

            actuals = {
                    api.ActualsType.Points: [],
                    api.ActualsType.Buffered: [],
                }

            for month in range(ged_start.month,ged_end.month+1):
                actuals[api.ActualsType.Points].append(ged_api.get_points(
                        gwno,year=ged_end.year,month=month))
                actuals[api.ActualsType.Buffered].append(ged_api.get_buffered(
                        gwno,year=ged_end.year,month=month))

            for t in (api.ActualsType.Points,api.ActualsType.Buffered):
                actuals[t] = reduce(feature_collection_union,actuals[t])

            for prediction in preds["features"]:
                for metric,required_type in config.METRICS:
                    exists = (session
                            .query(models.Metric)
                            .get((int(prediction["id"]),metric.__name__))
                        ) is not None

                    if not exists:
                        logger.info("Computing metric %s for %s",
                                metric.__name__,
                                prediction["id"]
                            )
                        metric = models.Metric.compute(
                                session,metric,prediction,actuals[required_type])
                        session.add(metric)
                    else:
                        logger.info("Metric %s for %s exists",
                                metric.__name__,
                                prediction["id"]
                            )
            logger.info("Adding metrics for %s",gwno)
            session.commit()
