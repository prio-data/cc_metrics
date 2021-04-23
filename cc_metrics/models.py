
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from . import db

meta = sa.MetaData()
Base = declarative_base(metadata=meta)

shapes = sa.Table("api_shape",Base.metadata,autoload_with=db.engine)

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
