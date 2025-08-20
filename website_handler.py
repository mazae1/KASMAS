import os
import json
import shutil

with open('config.json') as cnfgfl:
    config = json.load(cnfgfl)

server_src = 'website/'
index_file = os.path.join(server_src, 'index.html')
data_file = 'storage.json'

server_dest = config['server_folder']

def update_website():
    shutil.copy(index_file, os.path.join(server_dest, 'index.html'))
    shutil.copy(data_file, os.path.join(server_dest, 'storage.json'))

update_website()