# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 11:21:15 2023

@author: Alycia Leonard, University of Oxford

spatial_data_prep.py

This script joins the outputs from GLAES to the hexagons produced by SPIDER for input to GEOH2.
The inputs are the SPIDER hex.geojson file and the GLAES pv_placements.shp and turbine_placements.shp files
The output is a hexagon file where a count of turbine and pv installations is attached to the hexagons saved in Data.

"""

import geopandas as gpd

# Define country name (used for output filenames)
country_names = ["Algeria", "Angola", "Dem. Rep. Congo", "Cabo Verde", "Djibouti", "Egypt", "Kenya", "Mauritania",
                 "Morocco", "Namibia", "South Africa"]

# create a for loop that can loop through a list of country names
for country_name in country_names:

    print(f"Combining GLAES and SPIDER data for {country_name}!")

    # Get country name with no spaces or periods to load SPIDER files
    country_name_nospace = country_name.replace(" ", "")
    country_name_nospace = country_name_nospace.replace(".", "")

    # Load all files and convert all to the country's CRS
    print(" - Loading files...")
    hex = gpd.read_file(f"C:\\Users\\lahert5576\\PycharmProjects\\ccg-spider\\prep\\processed\\{country_name_nospace}_hex.geojson")
    wind_points = gpd.read_file(f"C:\\Users\\lahert5576\\PycharmProjects\\glaes\\results\\{country_name}_turbine_placements_4MW.shp")
    pv_points = gpd.read_file(f"C:\\Users\\lahert5576\\PycharmProjects\\glaes\\results\\{country_name}_pv_placements.shp")
    hex.to_crs(pv_points.crs, inplace=True)

    print(" - Joining turbine locations...")
    # Spatial join the wind points to the polygons
    spatial_join = gpd.sjoin(wind_points, hex, how='left', op='within')

    # Group by polygon and count the points within each polygon
    wind_point_counts = spatial_join.groupby('index_right').size()

    # Merge the point counts with the 'hex' GeoDataFrame based on the index
    hex['theo_turbines'] = wind_point_counts

    # If some polygons have no points, fill their 'point_count' with 0
    hex['theo_turbines'].fillna(0, inplace=True)

    print(" - Joining pv locations...")
    # Spatial join the pv points to the polygons
    spatial_join = gpd.sjoin(pv_points, hex, how='left', op='within')

    # Group by polygon and count the points within each polygon
    pv_point_counts = spatial_join.groupby('index_right').size()

    # Merge the point counts with the 'hex' GeoDataFrame based on the index
    hex['theo_pv'] = pv_point_counts

    # If some polygons have no points, fill their 'point_count' with 0
    hex['theo_pv'].fillna(0, inplace=True)

    print(" - Done! Saving to GeoJSON.")
    # Save the file
    hex.to_file(f'C:\\Users\\lahert5576\\PycharmProjects\\GeoNH3\\Data\\{country_name_nospace}_hex_final.geojson', driver='GeoJSON', encoding='utf-8')

