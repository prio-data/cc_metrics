
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
import numpy as np
from toolz.functoolz import curry,compose
from shapely.geometry import shape
from . import models,spatial

def date_filtered(start_date,end_date,query):
    if start_date:
        query = query.filter(models.Shape.date >= start_date)
    if end_date:
        query = query.filter(models.Shape.date <= end_date)
    return query

def country_filtered(country,query):
    if country:
        query = query.filter(models.Shape.country_id == country)
    return query

def user_only(user,query):
    return query.filter(models.Shape.author_id == user)

def metric_countries_in_span(session:Session, user:int, start_date:date=None, end_date:date=None):
    query = compose(
            curry(date_filtered)(start_date,end_date),
            curry(user_only)(user),
            lambda q: q.distinct(),
            lambda q: q.join(models.Metric),
            lambda q: q.query(models.Shape.country_id),
        )(session)

    return [dict(r) for r in query.all()]

def summary(
        session:Session, 
        user:int, 
        start_date:Optional[date] = None, 
        end_date:Optional[date] = None,
        country: Optional[int] = None):

    results = {}

    def metric_query(session,metric_name):
        op = compose(
                curry(country_filtered)(country),
                curry(date_filtered)(start_date,end_date),
                curry(user_only)(user),
                lambda q: q.join(models.Shape),
                lambda q: q.filter(models.Metric.name == metric_name),
                lambda q: q.query(models.Metric.value),
            )
        return np.array([*op(session).all()])

    metric_query = curry(metric_query,session)

    def maybe_metric_query(metric,operation):
        metrics = metric_query(metric)
        if len(metrics) > 0:
            return getattr(metrics,operation)()
        else:
            return None

    operations = {
            "predicted_area": lambda: maybe_metric_query("square_km_area","sum"),
            "conflict_coverage": lambda: maybe_metric_query("conflict_coverage","mean"),
            "accuracy": lambda: maybe_metric_query("correct","mean"),
        }

    shapes = compose(
            curry(country_filtered)(country),
            curry(date_filtered)(start_date,end_date),
            curry(user_only)(user),
            lambda q: q.query(models.Shape.shape)
        )(session).all()
    
    shapes = [row["shape"]["geometry"] for row in shapes]
    
    shapes = [*shapes]
    results["shapes"] = len(shapes)

    ops_if_shapes = ("conflict_coverage","predicted_area","accuracy")
    if results["shapes"] > 0:
        for k in ops_if_shapes:
            results[k] = operations[k]()
    else:
        for k in ops_if_shapes:
            results[k] = None 

    results = {k:v for k,v in results.items() if not v is None}

    return results 
