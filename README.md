# KPIS_data
Data processing utilities for KPIS Challenge

TODO: we need to define end-to-end workflow for data curation. Currently, we use several scripts for processing raw data.

## Scripts description:

- 1. ```Save_geojson.groovy```: This is used in QuPath, to export annotations as contours, then saved to JSON files with coordinates.

- 2. ```draw_contour_with4points_scn.py```: This script is used for converting contours JSON file to binary mask.

- 3. ```KPIS_CZI_patchCrop.py```: The script used to crop patches from CZI file. 

- 4. ```movefile.py```: Find only the patches with foregrounds, remove empty tiles.
