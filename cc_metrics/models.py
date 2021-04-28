
import pickle
import logging
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from azure_blob_storage_cache.exceptions import NotCached
from . import db,config


try:
    meta = config.general_cache["metrics-db-reflection"]
    shapes = meta.tables["api_shape"]
except NotCached:
    logging.critical("Reflecting tables from DB")
    meta = sa.MetaData()
    shapes = sa.Table("api_shape",meta,autoload_with=db.engine)
    config.general_cache["metrics-db-reflection"] = meta

Base = declarative_base(metadata=meta)

class Shape(Base):
    __table__ = shapes

class Metric(Base):
    __tablename__ = "evaluation_metric"

    shape_id = sa.Column(sa.Integer,sa.ForeignKey("api_shape.id"),primary_key=True)
    shape = relationship(Shape)
    name = sa.Column(sa.String,primary_key=True)

    value = sa.Column(sa.Float)

    @classmethod
    def compute(cls,session,function,prediction,actuals):
        metric_name = function.__name__
        shape = session.query(Shape).get(prediction["id"])
        if shape is None:
            raise KeyError(f"Prediction {prediction['id']} not found in DB")
        value = function(prediction,actuals)
        return cls(
                name = metric_name,
                value = value,
                shape = shape
            )

    def __str__(self):
        return f"{self.shape.id}s {self.name}: {self.value}"
