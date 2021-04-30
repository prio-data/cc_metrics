from shapely import ops,geometry
import pyproj
import utm_zone

PROJ = {
        "WSG84":"+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
    }

ftr_wrap = lambda shply: {"type":"Feature","geometry":geometry.mapping(shply)}

def shapely_to_geojson(shapes):
    def shape_to_feature(shape):
        return {
                "type":"Feature",
                "geometry":dict(geometry.mapping(shape)),
                "properties":{}
            }

    return {
            "type":"FeatureCollection",
            "features": [shape_to_feature(shp) for shp in shapes]
        }

def square_km_area(feature):
    shape = geometry.shape(feature["geometry"])
    centroid_utm = utm_zone.proj(
                ftr_wrap(shape.centroid)
            )
    transformer = pyproj.Transformer.from_proj(PROJ["WSG84"],centroid_utm)
    utm_shape = ops.transform(transformer.transform,shape)
    return utm_shape.area / 1e6
