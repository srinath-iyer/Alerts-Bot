import requests
import folium
from selenium import webdriver
from folium.rasterize import rasterize
r=requests.get("https://nominatim.openstreetmap.org/search?q="+"Durham+NC"+"&format=json", headers={"User-Agent":"Alerts-Discord-Bot"}).json()
m=folium.Map(location=[r[0]['lat'],r[0]['lon']])
rasterize(m, 'map.png')