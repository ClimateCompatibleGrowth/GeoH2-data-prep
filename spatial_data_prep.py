# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 14:30:10 2023

@author: Alycia Leonard, University of Oxford

spatial_data_prep.py

This script prepares raw spatial data for land exclusion in GLAES and hexagon preparation in SPIDER.
The raw inputs should be downloaded to /Raw_Spatial_Data before execution.
The outputs are saved in /Inputs_Glaes/data and /Inputs_Spider/data respectively.

"""

import time
import os
import geopandas as gpd
import pickle
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
from unidecode import unidecode

# Record the starting time
start_time = time.time()

# Define country name (used for output filenames)
country_names = ["REPLACE", "WITH", "COUNTRY", "NAMES"]

# Get paths to data files
dirname = os.path.dirname(__file__)
data_path = os.path.join(dirname, 'Raw_Spatial_Data')
regionPath = os.path.join(data_path, 'ne_50m_admin_0_countries', 'ne_50m_admin_0_countries.shp')
clcRasterPath = os.path.join(data_path, "PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif")
oceanPath = os.path.join(data_path, "GOaS_v1_20211214_gpkg", "goas_v01.gpkg")
OSM_path = os.path.join(data_path, "OSM")

# Define output directories
glaes_output_dir = os.path.join(dirname, 'Inputs_Glaes', 'data')
os.makedirs(glaes_output_dir, exist_ok=True)
spider_output_dir = os.path.join(dirname, 'Inputs_Spider', 'data')
os.makedirs(spider_output_dir, exist_ok=True)

# Read shapefile of countries
countries = gpd.read_file(regionPath).set_index('NAME')

# create a for loop that can loop through a list of country names
for country_name in country_names:
    print("Prepping " + country_name + "...")

    # Get country names without accents, spaces, apostrophes, or periods for saving files
    country_name_clean = unidecode(country_name)
    country_name_clean = country_name_clean.replace(" ", "")
    country_name_clean = country_name_clean.replace(".", "")
    country_name_clean = country_name_clean.replace("'", "")

    # grab country boundaries
    country = countries.loc[[f'{country_name}'], :]

    # calculate UTM zone based on representative point of country
    representative_point = country.representative_point().iloc[0]
    latitude, longitude = representative_point.y, representative_point.x
    EPSG = int(32700 - round((45 + latitude) / 90, 0) * 100 + round((183 + longitude) / 6, 0))
    with open(os.path.join(glaes_output_dir, f'{country_name_clean}_EPSG.pkl'), 'wb') as file:
       pickle.dump(EPSG, file)

    # reproject country to UTM zone
    country.to_crs(epsg=EPSG, inplace=True)
    country.to_file(os.path.join(glaes_output_dir, f'{country_name_clean}.geojson'), driver='GeoJSON', encoding='utf-8')

    # Buffer the "country" polygon by 1000 meters to create a buffer zone
    country_buffer = country['geometry'].buffer(10000)
    country_buffer.make_valid()
    country_buffer.to_file(os.path.join(glaes_output_dir, f'{country_name_clean}_buff.geojson'), driver='GeoJSON', encoding='utf-8')

    # Reproject GOAS to UTM zone of country
    GOAS = gpd.read_file(oceanPath)
    country_buffer = country_buffer.to_crs(epsg=4326)
    GOAS.to_crs(epsg=4326, inplace=True)
    GOAS_country = gpd.clip(GOAS, country_buffer)
    GOAS_country['geometry'].make_valid()
    # Reconvert to country CRS? Check it makes no difference in distance outputs. GLAES seems happy with 4326.
    GOAS_country.to_file(os.path.join(glaes_output_dir, f'{country_name_clean}_oceans.geojson'), driver='GeoJSON', encoding='utf-8')

    # Get country names without accents, spaces, apostrophes, or periods
    country_name_clean = unidecode(country_name)
    country_name_clean = country_name_clean.replace(" ", "")
    country_name_clean = country_name_clean.replace(".", "")
    country_name_clean = country_name_clean.replace("'", "")

    # Save oceans to gpkg for spider
    GOAS_country.to_file(os.path.join(spider_output_dir, f'{country_name_clean}_oceans.gpkg'), driver='GPKG', encoding='utf-8')

    # Save OSM layers in 4236 gpkgs for spider
    OSM_country_path = os.path.join(OSM_path, f"{country_name_clean}")

    OSM_waterbodies = gpd.read_file(os.path.join(OSM_country_path, 'gis_osm_water_a_free_1.shp'))
    OSM_waterbodies.to_file(os.path.join(spider_output_dir, f'{country_name_clean}_waterbodies.gpkg'), driver='GPKG', encoding='utf-8')
    OSM_roads = gpd.read_file(os.path.join(OSM_country_path, f'gis_osm_roads_free_1.shp'))
    OSM_roads.to_file(os.path.join(spider_output_dir, f'{country_name_clean}_roads.gpkg'), driver='GPKG', encoding='utf-8')
    OSM_waterways = gpd.read_file(os.path.join(OSM_country_path, 'gis_osm_waterways_free_1.shp'))
    OSM_waterways.to_file(os.path.join(spider_output_dir, f'{country_name_clean}_waterways.gpkg'), driver='GPKG', encoding='utf-8')

    # Convert country back to EPSC 4326 to trim CLC and save this version for SPIDER as well
    country.to_crs(epsg=4326, inplace=True)
    country.to_file(os.path.join(spider_output_dir, f'{country_name_clean}.gpkg'), driver='GPKG', encoding='utf-8')

    # Open the CLC GeoTIFF file for reading
    with rasterio.open(clcRasterPath) as src:
        # Mask the raster using the vector file's geometry
        out_image, out_transform = mask(src, country.geometry.apply(mapping), crop=True)
        # Copy the metadata from the source raster
        out_meta = src.meta.copy()
        # Update the metadata for the clipped raster
        out_meta.update({
            'height': out_image.shape[1],
            'width': out_image.shape[2],
            'transform': out_transform
        })

        # Save the clipped raster as a new GeoTIFF file
        with rasterio.open(os.path.join(glaes_output_dir, f'{country_name_clean}_CLC.tif'), 'w', **out_meta) as dest:
            dest.write(out_image)

    print("Done!")

