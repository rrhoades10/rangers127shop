import requests
import requests_cache
import decimal 
import json 




requests_cache.install_cache(cache_name = 'image_cache', backend='sqlite', expire_after=900)




def get_image(search):

    url = "https://google-search72.p.rapidapi.com/search"

    querystring = {"q": search,"gl":"us","lr":"lang_en","num":"1","start":"0"}

    headers = {
        "X-RapidAPI-Key": "a545654756msh41215968af0133ap15acf5jsneb67a6cb1e2e",
        "X-RapidAPI-Host": "google-search72.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()
    img_url = data['items'][0]['originalImageUrl'] #traversing data dictionary to get the image url we want
    return img_url

class JSONENcoder(json.JSONEncoder):
    def default(self, obj): #our custom method to handle encoding decimal objects 
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return json.JSONEncoder(JSONENcoder, self).default(obj) #if its not a decimal just pass it to the default on the json.JSONEncoder