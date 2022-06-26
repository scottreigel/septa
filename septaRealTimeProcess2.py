from ftplib import FTP
import requests
import pandas as pd
import json
import geopandas
import time

host = "your_host"
user = "your_name"
password = "your_password"

def septa_json():
    url = 'http://www3.septa.org/hackathon/TransitViewAll/'
    septa = requests.get(url).json()
    
    septa=(septa['routes'])
    septa = septa[0]
    df = pd.concat({k: pd.Series(v) for k, v in septa.items()}).reset_index()
    df.columns = ['routes', 'content', 'content1']
    septa=pd.json_normalize(json.loads(df.to_json(orient='records')))
    
    septa['latitude'] = septa['content1.lat'].astype(float)
    septa['longitude'] = septa['content1.lng'].astype(float)
    septa['dest'] = septa['content1.destination'].astype(str)
    septa['direction'] = septa['content1.Direction'].astype(str)
    septa['nextstop'] = septa['content1.next_stop_name'].astype(str)
    
    cols = ['routes', 'latitude', 'longitude', 'dest', 'direction', 'nextstop']
    
    septa = septa[cols]
    gdf = geopandas.GeoDataFrame(septa, geometry=geopandas.points_from_xy(septa.longitude, septa.latitude))
    return gdf.to_file('septa.json', driver="GeoJSON")
	
def ftp_process():
    with FTP(host) as ftp:
        ftp.login(user=user, passwd=password)
    
        ftp.cwd('public_html')
        with open('septa.json', 'rb') as f:
            ftp.storbinary("STOR " + "septa.json", f)
            
def septa_process():
    septa_json()
    ftp_process()
    
 
while(True):
    septa_process()
    time.sleep(6)