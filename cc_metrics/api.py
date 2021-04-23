import logging
from typing import Optional
from datetime import date
import os
from enum import Enum
from urllib.parse import urlencode
import requests

logger = logging.getLogger(__name__)

class Api:
    def __init__(self,url):
        self.url = url

    def rel_url(self,path):
        return os.path.join(self.url,path)

    def fetch_json(self,*args,**kwargs):
        path = os.path.join(*[str(e) for e in args])

        url = self.rel_url(path)

        pstring = urlencode({str(k):str(v) for k,v in kwargs.items()})
        if pstring:
            url += "?"+pstring
        logger.debug("%s getting %s",self.__class__,url)
        return requests.get(url).json()

class Predictions(Api):
    def get(self, 
            user:Optional[int]=None, 
            start_date:Optional[date]=None,
            end_date:Optional[date]=None, 
            country:Optional[int]=None):

        args = {
            "start_date":start_date,
            "end_date":end_date,
            "user":user,
            "country":country
            }

        args = {k:v for k,v in args.items() if v is not None}

        return self.fetch_json("shapes",**args)

class Ged(Api):
    def get_points(self, country:int, year:int, quarter:int):
        return self.fetch_json(country,year,quarter,"points")

    def get_buffered(self, country:int, year:int, quarter:int, buffer:int):
        return self.fetch_json(country,year,quarter,"buffered",buffer)
