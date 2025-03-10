# -*- coding: utf-8 -*- 
"""
Created on Tue Aug 6 11:32:11 2024

@author: Lukas Schirren, Imperial College London

This script prepares raw spatial data for hexagon preparation in SPIDER by creating a geopackage file.
The raw inputs should be downloaded to /Raw_Spatial_Data before execution.
The outputs are saved in /Inputs_Spider/data.

"""

import os
import pandas as pd 
import geopandas as gpd
from pyproj import Transformer

# Function to convert each coordinate
def convert_coordinates(easting, northing):
    longitude, latitude = transformer.transform(easting, northing)
    return latitude, longitude


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    input_path = os.path.join(script_dir, "Raw_Spatial_Data", "19.7.2024-NEW UPDATED_Data_lao_231223_NPP_coordinate.xlsx")
    output_dir = os.path.join(script_dir, "Inputs_Spider", "data")
    os.makedirs(output_dir, exist_ok=True) 
    output_path = os.path.join(output_dir, "hydropower_dams.gpkg")

    data = pd.read_excel(input_path, 'NPDP power plant info')

    data = data[['SNo', 'East E', 'North N', 'Status', 'PP name', 'Fuel Type',
        'Province', 'Region', 'Total capacity (MW)',
        'Domestic Capacity (MW)', 'Export Capacity (MW)',
        'Expected Generation (GWh)',
        'total theoretical possible generation (local) GWh', 'COD (Year)',
        'Exporting country country', 'Head Hydraulic (m)']]

    data['East E'] = pd.to_numeric(data['East E'], errors='coerce')
    data['North N'] = pd.to_numeric(data['North N'], errors='coerce')

    data = data.dropna(subset=['East E', 'North N'])
    transformer = Transformer.from_crs("epsg:32648", "epsg:4326", always_xy=True)

    converted_coords = data.apply(
        lambda row: convert_coordinates(row['East E'], row['North N']),
        axis=1
    )

    data = data.copy()
    data[['Latitude', 'Longitude']] = pd.DataFrame(converted_coords.tolist(), index=data.index)

    data = data.rename(columns={"Total capacity (MW)": "capacity",
                                   "COD (Year)": "COD",
                                   "Head Hydraulic (m)": "head"})
    data = data[data['Fuel Type'].isin(['Run - Off', 'Reservoir '])]
    data['capacity'] = pd.to_numeric(data['capacity'], errors='raise')
    data_existing = data[data['Status'].str.contains('Existing', na=False)]
    

    data_existing = data_existing.dropna(subset='head')
    print(f"Number of missing 'head' values: {data_existing['head'].isna().sum()}")

    gdf = gpd.GeoDataFrame(
        data_existing,
        geometry=gpd.points_from_xy(data_existing.Longitude, data_existing.Latitude)
    )

    gdf.set_crs(epsg=4326, inplace=True)
    gdf.to_file(output_path, layer='dams', driver="GPKG")

    relative_output_path = os.path.relpath(output_path, script_dir)
    print(f"GeoPackage file successfully created at: {relative_output_path}")
