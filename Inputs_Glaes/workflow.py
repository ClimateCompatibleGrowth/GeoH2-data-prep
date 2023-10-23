import glaes as gl
import time
import os
import pickle

# Record the starting time
start_time = time.time()

# Define turbine radius in meters for spacing
d = 150  # NREL_ReferenceTurbine_2020ATB_4MW - https://nrel.github.io/turbine-models/2020ATB_NREL_Reference_4MW_150.html
# d = 80 # Vestas_V80_2MW_gridstreamer - https://en.wind-turbine-models.com/turbines/19-vestas-v80-2.0
# d = 127 # Enercon_E126_7500kW - https://www.thewindpower.net/turbine_en_225_enercon_e126-7500.php

# Load data files for region
data_path = 'C:\\Users\\lahert5576\\PycharmProjects\\glaes\\data\\'

# Output directory
output_dir = 'C:\\Users\\lahert5576\\PycharmProjects\\glaes\\results\\'
os.makedirs(output_dir, exist_ok=True)

# Define country name (used for output filenames)
country_names = ["Algeria", "Angola", "Dem. Rep. Congo", "Cabo Verde", "Djibouti", "Egypt", "Kenya", "Mauritania",
                 "Morocco", "Namibia", "South Africa"]

# create a for loop that can loop through a list of country names

for country_name in country_names:

    print("Land exclusions for " + country_name)

    # Load the pickled EPSG code for the country
    with open(data_path + f'{country_name}_EPSG.pkl', 'rb') as file:
        EPSG = pickle.load(file)

    # %%% calculating exclusions

    print(" - Initializing exclusion calculator...")
    ec = gl.ExclusionCalculator(data_path + f'{country_name}.geojson', srs=EPSG, pixelSize=100)
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Applying exclusions - coast...")
    ec.excludeVectorType(data_path + f'{country_name}_oceans.geojson', buffer=250)
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Applying exclusions - protected areas...")
    ec.excludeVectorType(data_path + f'{country_name}_protected_areas.geojson', buffer=250)
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Applying exclusions - herbaceous wetland...")
    ec.excludeRasterType(data_path + f'{country_name}_CLC.tif', value=90, prewarp=True)
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Applying exclusions - built-up area...")
    ec.excludeRasterType(data_path + f'{country_name}_CLC.tif', value=50, prewarp=True)
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Applying exclusions - permanent water bodies...")
    ec.excludeRasterType(data_path + f'{country_name}_CLC.tif', value=80, prewarp=True)
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Saving excluded areas for wind as .tif file...")
    ec.save(output_dir + f'{country_name}_wind_exclusions.tif', overwrite=True)
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Distributing turbines and saving placements as .shp...")
    ec.distributeItems(separation=(d * 10, d * 5), axialDirection=45, output=output_dir + f'{country_name}_turbine_placements_4MW.shp')
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Applying exclusions - agriculture...")
    ec.excludeRasterType(data_path + f'{country_name}_CLC.tif', value=40, prewarp=True)
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Saving excluded areas for PV as .tif file...")
    ec.save(output_dir + f'{country_name}_pv_exclusions.tif', overwrite=True)
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

    print(" - Distributing pv plants and saving placements as .shp...")
    ec.distributeItems(separation=440, output=output_dir + f'{country_name}_pv_placements.shp')
    current_time = time.time() - start_time
    print(f"   Done! Time elapsed so far: {current_time:.4f} seconds")

