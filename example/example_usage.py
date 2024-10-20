from fuzzy_viewshed_calculator import FuzzyViewshedCalculator

# Define input parameters
input_vector = 'polygons.shp' #path to vectorial file, accepts shapefile, geopackage, etc.
dem_path = 'dem.tif' #path to DEM
output_folder = 'output/'
b1_value = 1000  # meters
observer_height = 1.65  # meters
max_distance = 5000  # meters, set to None if you don't want to limit the radius

# Create an instance of FuzzyViewshedCalculator
calculator = FuzzyViewshedCalculator(
    dem_path=dem_path,
    output_folder=output_folder,
    b1=b1_value,
    observer_height=observer_height,
    max_distance=max_distance
)

# Process the input vector file
calculator.process_vector_file(input_vector)

print("Fuzzy viewshed calculation completed.")
