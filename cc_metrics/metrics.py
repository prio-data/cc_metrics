from collections import defaultdict
from functools import reduce,partial
from shapely.geometry import shape,mapping
import pyproj
import utm_zone
from . import spatial

def identity(x,y):
    return .5

def all_actuals(prediction,points):
    pred_shape = shape(prediction["geometry"])
    actual = defaultdict(int)
    for key in ["low","best","high"]:
        actual[key] += 0
    for point in points["features"]:
        if pred_shape.contains(shape(point["geometry"])):
            for key in ["low","best","high"]:
                actual[key] += point["properties"][key]
    return actual

def all_discrepancies(prediction,buffered_points):
    actual = all_actuals(prediction,buffered_points) 
    discrepancies = dict()
    lower,upper = (prediction["properties"]["casualties"][k] for k in ("lower","upper"))

    for k,v in actual.items():
        if v < lower:
            discrepancies[k] = abs(v - lower)
        elif upper is not None and v > upper:
            discrepancies[k] = abs(v - upper)
        else:
            discrepancies[k] = 0
    return discrepancies 

def correct(prediction,buffered_points,kind="best"):
    return int(all_discrepancies(prediction,buffered_points)[kind] == 0)

def discrepancy(prediction,buffered_points,kind="best"):
    return all_discrepancies(prediction,buffered_points)[kind]

def actuals(prediction,points,kind="best"):
    return all_actuals(prediction,points)[kind]

def conflict_coverage(prediction,buffered_points):
    null_prediction = prediction["properties"]["intensity"] <= 0
    if buffered_points["features"]:
        pred_shape = shape(prediction["geometry"])
        points_shapes = [shape(pt["geometry"]) for pt in buffered_points["features"]]

        shp_union = reduce(lambda x,y: x.union(y), points_shapes)
        if not pred_shape.is_valid:
            pred_shape = pred_shape.buffer(0)

        covers = pred_shape.intersection(shp_union)
        cover_pst = covers.area / pred_shape.area 
        if not null_prediction:
            return cover_pst
        else:
            return 1 - cover_pst
    else:
        if null_prediction:
            return 1
        else:
            return 0

def square_km_area(prediction,*_,**__):
    return spatial.square_km_area(prediction)
