# KPIS_data
Data processing utilities for KPIS Challenge

TODO: we need to define end-to-end workflow for data curation. Currently, we use several scripts for processing raw data.

## Scripts description:

- 1. ```Save_geojson.groovy```: This is used in QuPath, to export annotations as contours, then saved to JSON files with coordinates.

- 2. ```draw_contour_with4points_scn.py```: This script is used for converting contours JSON file to binary mask.

- 3. ```KPIS_CZI_patchCrop.py```: The script used to crop patches from CZI file. 

- 4. ```movefile.py```: Find only the patches with foregrounds, remove empty tiles.



## Subject CZI read scenes:


- DN
  - 11-356: scene 0
  - 11-357: scene 1
  - 11-358: scene 0
  - 11-367: scene 0
  - 11-370: scene 0


- 56Nx
  - 12-116: scene 2
  - 12-117: scene 1
  - 12-169: scene 1
  - 12-170: scene 2
  - 12-171: scene 1

- Normal:
  - F4: scene 0
  - F2: scene 1
  - F1: scene 0
  - F3: scene 3
  - F1576: scene 1
