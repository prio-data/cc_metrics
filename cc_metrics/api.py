import logging
from typing import Optional
from datetime import date
import os
from enum import Enum
from urllib.parse import urlencode
import requests

logger = logging.getLogger(__name__)

class DoesNotExist(KeyError):
    pass

class ActualsType(Enum):
    Points = 1
    Buffered = 2

class Api:
    def __init__(self,url):
        self.url = url
        self.memcache = dict()

    def rel_url(self,path):
        return os.path.join(self.url,path)

    def fetch_json(self,*args,**kwargs):
        response = requests.get(self.make_url(*args,**kwargs))
        if response.status_code != 200:
            raise requests.HTTPError(response=response)
        else:
            return response.json()

    def make_url(self,*args,**kwargs):
        path = os.path.join(*[str(e) for e in args])
        url = self.rel_url(path)
        pstring = urlencode({str(k):str(v) for k,v in kwargs.items()})
        if pstring:
            url += "?"+pstring
        return url

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
    def get(self,type:ActualsType,*args,**kwargs):
        fetchers = {
                ActualsType.Points: self.get_points,
                ActualsType.Buffered: self.get_buffered,
            }
        return fetchers[type](*args,**kwargs)

    def fetch_json(self,*args,**kwargs):
        try:
            return super().fetch_json(*args,**kwargs)
        except requests.HTTPError as httpe:
            if httpe.response.status_code == 404:
                raise DoesNotExist(self.make_url(*args,**kwargs))
            else:
                raise httpe

    def get_points(self, country:int, year:int, quarter:int):
        return self.fetch_json(country,year,quarter,"points")

    def get_buffered(self, country:int, year:int, quarter:int, buffer:int=50000):
        return self.fetch_json(country,year,quarter,"buffered",buffer)
