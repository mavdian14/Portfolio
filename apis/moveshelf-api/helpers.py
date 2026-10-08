import os
import logging
import requests
import json
import pandas as pd

#return a logger that is the root logger of 'moveshelf-api' hierarchy
logger = logging.getLogger('moveshelf-api')

class Helpers:

    #returns a static method for a timeToCycle    
    @staticmethod
    def timeToCycle(series):
        series = (series - series.min()) / (series.max() - series.min())
        return series * 100

    
    @staticmethod
    def download_file(url, local_filename):
        #with to replace try-catch block more concisely
        with requests.get(url, stream=True) as r:
            #raise_for_status() returns an HTTPError object if an error has occurred
            r.raise_for_status()
            #open "local_filename"
            with open(local_filename, 'wb') as f:
                # iter.content() iterates over the response content
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush()
        return local_filename
   
    @staticmethod
    def parseParametersFile(paramsFile):
        with open(paramsFile) as f:
          #returm json object of paramsFile
          params = json.load(f)
    
        params_df = pd.DataFrame.from_dict(params['data'])
        values_df = params_df['values'].apply(pd.Series)
        params_df = pd.concat([ params_df.drop(['values'], axis=1), values_df], axis=1)
    
        return params_df

    @staticmethod
    def parseEventFile(eventsFile):
        with open(eventsFile) as f:
          events = json.load(f)

        #return a df of dict events['events']
        return pd.DataFrame.from_dict(events['events'])

    @staticmethod
    def parseKinematicsFile(kinematicsFile):
        with open(kinematicsFile) as f: #let's open and parse kinamatic angles 
          kin = json.load(f)
      
        return pd.DataFrame.from_dict(kin['data']) #create a panda DataFrame for easy manipulation
    
    @staticmethod
    def downloadDataToPath(data, dirpath):
        for d in data:
            url = d['previewDataUri']
            filename = d['originalFileName']
            #check if dirpath path doesn't exist
            if not os.path.exists(dirpath):
                #create dirpath directory recursively
                os.makedirs(dirpath)

            if d['dataType'] != 'video' and d['dataType'] != 'motion':
                #downloads url; optionally caches the result
                Helpers.download_file(url, dirpath + '/' + filename)
