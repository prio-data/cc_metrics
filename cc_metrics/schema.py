from typing import Dict,Union
from pydantic import BaseModel

class Report(BaseModel):
    metrics: Dict[str,Union[float,int]]
    country: int
    user: int

class QuarterlyReport(Report):
    year: int
    quarter: int

class Summary(Report):
    pass

class YearlySummary(Report):
    year: int

