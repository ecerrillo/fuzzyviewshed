import numpy as np
import geopandas as gpd
import rasterio
from fiona.crs import from_epsg
from shapely.geometry import Point, Polygon, MultiPolygon
from whitebox import WhiteboxTools
from scipy.spatial import distance
from itertools import combinations
import os
import tempfile

class FuzzyViewshedCalculator:
    def __init__(self, dem_path, output_folder, b1=1000, observer_height=1.65, max_distance=None):
        self.dem_path = dem_path
        self.output_folder = output_folder
        self.b1 = b1  # in meters
        self.observer_height = observer_height
        self.max_distance = max_distance
        self.wbt = WhiteboxTools()
        self.wbt.set_verbose_mode(False)
        self.wbt.set_working_dir(output_folder)

    def create_euclidean_distance_map(self, x_point, y_point, output_raster):
        """Create a Euclidean distance map from a given point."""
        with rasterio.open(self.dem_path) as src:
            meta = src.meta.copy()
            res_x, res_y = src.res

            rows, cols = np.indices((src.height, src.width), dtype=float)
            x_coords = cols * res_x + src.bounds.left
            y_coords = rows * -res_y + src.bounds.top

            distances = np.sqrt((x_coords - x_point) ** 2 + (y_coords - y_point) ** 2)

            meta.update(dtype=rasterio.float32, count=1)

            with rasterio.open(output_raster, 'w', **meta) as dst:
                dst.write(distances.astype(rasterio.float32), 1)

    def calculate_b2(self, object_width, visual_arc=1, distance_multiplier=3440):
        """Calculate b2 parameter for fuzzy viewshed."""
        a = object_width * distance_multiplier
        b2 = max(a - self.b1, 1)
        print(f'size = {object_width}, b2 = {b2}')
        return b2

    def create_fuzzy_viewshed(self, x_point, y_point, size, id):
        """Create a fuzzy viewshed for a given point."""
        b2 = self.calculate_b2(size)

        with tempfile.TemporaryDirectory() as tmpdir:
            euclidean_distance_path = os.path.join(tmpdir, f'disteuc_{id}.tif')
            viewshed_path = os.path.join(tmpdir, f'viewshed_{id}.tif')
            point_shp = os.path.join(tmpdir, f'point_{id}.shp')

            self.create_euclidean_distance_map(x_point, y_point, euclidean_distance_path)

            point = Point(x_point, y_point)
            gdf = gpd.GeoDataFrame(geometry=[point])
            gdf.crs = from_epsg(25830)
            gdf.to_file(point_shp)

            self.wbt.viewshed(
                dem=self.dem_path,
                output=viewshed_path,
                stations=point_shp,
                height=self.observer_height
            )

            with rasterio.open(viewshed_path) as src_viewshed, rasterio.open(euclidean_distance_path) as src_distance:
                viewshed = (src_viewshed.read(1) > 0).astype(np.float32)
                distances = src_distance.read(1)
                
                # Apply maximum distance mask if specified
                if self.max_distance is not None:
                    mask = distances <= self.max_distance
                else:
                    mask = np.ones_like(distances, dtype=bool)
                
                fuzzy_membership = np.where(distances <= self.b1, 1, 1 / (1 + 2 * ((distances - self.b1) / b2) ** 2))
                fuzzy_viewshed = fuzzy_membership * viewshed * mask
                
                # Assign null values to areas outside the mask
                fuzzy_viewshed = np.where(mask, fuzzy_viewshed, np.nan)

                meta = src_viewshed.meta.copy()
                meta.update(dtype=rasterio.float32, count=1, nodata=np.nan)
                output_path = os.path.join(self.output_folder, f'fuzzy_viewshed_{id}.tif')
                with rasterio.open(output_path, 'w', **meta) as dst:
                    dst.write(fuzzy_viewshed, 1)

    @staticmethod
    def max_diameter(geometry):
        """Calculate the maximum diameter of a polygon or multipolygon."""
        max_dist = 0
        if isinstance(geometry, Polygon):
            points = list(geometry.exterior.coords)
            max_dist = FuzzyViewshedCalculator.calculate_max_distance(points)
        elif isinstance(geometry, MultiPolygon):
            for polygon in geometry.geoms:
                points = list(polygon.exterior.coords)
                current_max = FuzzyViewshedCalculator.calculate_max_distance(points)
                if current_max > max_dist:
                    max_dist = current_max
        return max_dist

    @staticmethod
    def calculate_max_distance(points):
        """Calculate the maximum distance between any two points."""
        return max(Point(p1).distance(Point(p2)) for p1, p2 in combinations(points, 2))

    def process_vector_file(self, vector_file):
        """Process a vector file and create fuzzy viewsheds for each feature."""
        points = gpd.read_file(vector_file)
        for _, point in points.iterrows():
            size = self.max_diameter(point.geometry)
            x = point.geometry.centroid.x
            y = point.geometry.centroid.y
            id = point['id']
            print(f"Processing point: id={id}, x={x}, y={y}, size={size}")
            self.create_fuzzy_viewshed(x, y, size, id)
