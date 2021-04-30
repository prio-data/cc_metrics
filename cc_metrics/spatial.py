from shapely.geometry import mapping

def shapely_to_geojson(shapes):
    def shape_to_feature(shape):
        return {
                "type":"Feature",
                "geometry":dict(mapping(shape)),
                "properties":{}
            }

    return {
            "type":"FeatureCollection",
            "features": [shape_to_feature(shp) for shp in shapes]
        }
