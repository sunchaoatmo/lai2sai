#!/usr/bin/env python3
from downloader import MODIS_download
import requests # get the requsts library from https://github.com/requests/requests
from bs4 import BeautifulSoup
hvs=set(['h11v06', 'h11v07', 'h11v04', 'h11v05', 'h11v03', 'h07v05', 'h07v04', 'h07v07', 'h07v06', 'h13v03', 'h13v04', 'h13v05', 'h14v03', 'h10v03', 'h10v05', 'h10v04', 'h10v07', 'h10v06', 'h09v03', 'h09v07', 'h09v06', 'h09v05', 'h09v04', 'h08v04', 'h08v05', 'h08v06', 'h08v07', 'h12v03', 'h14v04', 'h12v06', 'h12v05', 'h12v04', 'h06v06', 'h06v07'])
rooturl="https://e4ftl01.cr.usgs.gov/MOTA/MCD12Q1.006/"
result = requests.get(rooturl)
print(result.status_code)
# raise an exception in case of http errors
result.raise_for_status()  
c = result.content
soup = BeautifulSoup(c,"html.parser")
urls = []
for link in soup.findAll('a'):
  url=link.get("href")
  if url[0].isdigit():
      url=rooturl+url
      urls.append(url)
      print(url)
for url in urls:
  result = requests.get(url)
  print(result.status_code)
  # raise an exception in case of http errors
  result.raise_for_status()  
  c = result.content
  soup = BeautifulSoup(c,"html.parser")
  url_todownloads=[]
  for link in soup.findAll('a'):
     hdfurl=link.get("href")
     if hdfurl.endswith("hdf"):
       hv_temp=hdfurl.split(".")[2]
       if hv_temp in hvs:
         #url_todownloads.append(url)
         hdfurl=url+hdfurl
         print(hdfurl)
         MODIS_download(hdfurl)
