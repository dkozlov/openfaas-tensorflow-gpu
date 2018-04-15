import os
import tarfile
import six.moves.urllib as urllib
from settings import *
 
opener = urllib.request.URLopener() 
opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE) 
tar_file = tarfile.open(MODEL_FILE) 
for file in tar_file.getmembers(): 
  file_name = os.path.basename(file.name) 
  if 'frozen_inference_graph.pb' in file_name: 
    tar_file.extract(file, os.getcwd()) 
