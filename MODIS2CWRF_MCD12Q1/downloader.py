#!/usr/bin/env python3
import requests # get the requsts library from https://github.com/requests/requests
 
 
 
# overriding requests.Session.rebuild_auth to mantain headers when redirected
 
class SessionWithHeaderRedirection(requests.Session):
 
    AUTH_HOST = 'urs.earthdata.nasa.gov'
 
    def __init__(self, username, password):
 
        super().__init__()
 
        self.auth = (username, password)
 
  
 
   # Overrides from the library to keep headers when redirected to or from
 
   # the NASA auth host.
 
    def rebuild_auth(self, prepared_request, response):
 
        headers = prepared_request.headers
 
        url = prepared_request.url
 
  
 
        if 'Authorization' in headers:
 
            original_parsed = requests.utils.urlparse(response.request.url)
 
            redirect_parsed = requests.utils.urlparse(url)
 
  
 
            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
 
                del headers['Authorization']
 
  
 
        return
 
  
 
def MODIS_download(url):
# create session with the user credentials that will be used to authenticate access to the data
  username = "sunchao@umd.edu"
  password= "73Z-g9P-9zC-E4F"
  session = SessionWithHeaderRedirection(username, password)
# the url of the file we wish to retrieve
#url = "https://e4ftl01.cr.usgs.gov/MOLT/MOD44B.006/2000.03.05/MOD44B.A2000065.h13v02.006.2017081102411.hdf"
# extract the filename from the url to be used when saving the file
  filename = url[url.rfind('/')+1:]  
  try:
      # submit the request using the session
      response = session.get(url, stream=True)
      print(response.status_code)
      # raise an exception in case of http errors
      response.raise_for_status()  
      # save the file
      with open(filename, 'wb') as fd:
          for chunk in response.iter_content(chunk_size=1024*1024):
              fd.write(chunk)
  except requests.exceptions.HTTPError as e:
      # handle any errors here
      print(e)
