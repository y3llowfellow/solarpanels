#loading coordinates:
import numpy as np
import json
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import os
from git import Repo
import subprocess
import math

#REPLACE W/ YOUR DESIRED DESTINATION FOR THE RESULTS
output_file_path = "/Users/colinshen/Desktop"

try:
    os.mkdir(output_file_path+"/solardata")
    os.mkdir(output_file_path+"/solardata/yolo")
    os.mkdir(output_file_path+"/solardata/images")
    os.mkdir(output_file_path+"/solardata/output")
except:
    for root, dirs, files in os.walk(output_file_path+"/solardata", topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.mkdir(output_file_path + "/solardata/yolo")
    os.mkdir(output_file_path + "/solardata/images")
    os.mkdir(output_file_path + "/solardata/output")

#replace with file path of the geojson file of given coordinate areas that you want to scan
file_path = "/Users/colinshen/PycharmProjects/solar/allen_ufz/labels/labels/point_test.geojson"
with open(file_path, 'r') as file:
    geojson_data = json.load(file)

features = geojson_data.get('features', [])

x_coordinates = []
y_coordinates = []
for feature in features:
    properties = feature.get('properties', {})
    x_coordinates.append(properties.get('x_coordinates', []))
    y_coordinates.append(properties.get('y_coordinates', []))

coordinates = np.column_stack((y_coordinates, x_coordinates))
coordinate_tuples = [tuple(row) for row in coordinates.tolist()]

#function to display a satellite image from inputted coordinates
#boolean parameter download
def get_satellite_image(download,lat, lon, api_key, zoom=17, size="600x600", maptype="satellite"):
    url = "https://maps.googleapis.com/maps/api/staticmap"
    #parameters to download the image
    params = {
        "center": f"{lat},{lon}",
        "zoom": zoom,
        "size": size,
        "maptype": maptype,
        "key": api_key
    }
    response = requests.get(url, params=params)
    #Show image if retrieval is successful
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        #saves user-inputted region image to drive
        if download:
          filename = f"{lat}_{lon}.png"
          filepath = f"{output_file_path+'/solardata/images'}/{filename}"
          image.save(filepath)
    else:
        print("Failed to retrieve the image", response.status_code, response.text)
# Replace with your actual coordinates and API key
api_key ="AIzaSyCk2o1KkcXH8IPVpqLIoZk4XIAN4EIRtVw"
#downloads images of each desired region
for lat, lon in coordinates:
  get_satellite_image(True, lat, lon, api_key)


# Define the command and its arguments as a list
command = [
    "yolo", "segment", "predict",
    "model="+output_file_path+"/best.pt",
    "imgsz=640",
    "save=True",
    "save_txt=True",
    "save_conf=True",
    "source="+output_file_path+"/solardata/images",
    "project="+output_file_path+"/solardata/yolo/output",
    "name=segmentation_results"
]

# Execute the command
subprocess.run(command)




#converting txt file with yolo polygons into a 2d array
def extract_polygon_coords(yolo_file_path):
    polygon_coords = []
    try:
      with open(yolo_file_path, 'r') as file:
          for line in file:
              parts = line.strip().split()
              coords = parts[1:-1]
              polygon_coords.append([float(coord) for coord in coords])
    except:
        with open(yolo_file_path, 'w') as file:
          file.write(" ")
    return polygon_coords

def plot_polygons(yolo_file_path):
    all_x = []
    all_y = []
    #array of polygons
    polygons = extract_polygon_coords(yolo_file_path)
    for poly in polygons:
        x_coords = poly[::2] + [poly[0]]
        y_coords = poly[1::2] + [poly[1]]
        all_x.append(x_coords)
        all_y.append(y_coords)
    return all_x, all_y

def xyToGeo(x, y, lat, lon):
  w = 600
  h = 600
  zoom = 17
  parallelMultiplier = math.cos(lat * math.pi / 180)
  degreesPerPixelX = 360 / math.pow(2, zoom + 8)
  degreesPerPixelY = 360 / math.pow(2, zoom + 8) * parallelMultiplier
  pointLat = float(lat) - degreesPerPixelY * (y - h / 2)
  pointLng = float(lon) + degreesPerPixelX * ( x  - w / 2)
  return[pointLng, pointLat]


#each sattelite location
for lat, lon in coordinates:
  yolo_file_path = output_file_path+ '/solardata/yolo/output/segmentation_results/labels/'+str(lat)+'_'+str(lon)+'.txt'
  all_x, all_y = plot_polygons(yolo_file_path)
  convertedPolygons=[]
  geojsonString = '{"type": "FeatureCollection","features": ['
  #each polygon
  for j in range(len(all_x)):
    poly_x = all_x[j]
    poly_y = all_y[j]
    convertedPoints = []
    #each point in the polygon
    for i in range(len(poly_x)):
      relative_scaled_x = (600 * poly_x[i])
      relative_scaled_y = (600 * poly_y[i])
      convertedPoints.append(xyToGeo(relative_scaled_x, relative_scaled_y, lat, lon))
    geojsonString = geojsonString+ '{"type": "Feature","properties": {},"geometry": {"type": "Polygon","coordinates": ['
    geojsonString = geojsonString + str(convertedPoints) +']}},'

  geojsonString = geojsonString[:-1]
  geojsonString = geojsonString+"]}"
  file_path = output_file_path+"/solardata/output/"+str(lat)+"_"+str(lon)+".txt"
  with open(file_path, 'w') as file:
    file.write(geojsonString)
