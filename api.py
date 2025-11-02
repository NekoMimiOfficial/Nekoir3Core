import requests
from NekoMimi.reg import readCell

api= readCell("nekoir3c")

# def time_chatting(p: int):
#     sec= p
#     mins= 0
#     hours= 0
#     if sec >= 60:
#         mins= int(sec/60)
#     if mins >= 60:
#         hours= int(mins/60)
#
#     return f"{hours}:{mins%60}:{sec%60}"
#
#
# def get_track(term, api):
#     req= requests.get(url= api+ "/search/", params= {'s': term})
#     jsonObj= req.json()
#     if not "items" in jsonObj:
#         return False
#     items= jsonObj["items"]
#     if len(items) < 1:
#         return False
#     songID= items[0]["id"]
#     getUrlPlayable= requests.get(url= api+ "/track/", params= {'id': songID, 'quality': 'LOW'})
#     gson= getUrlPlayable.json()
#     if not len(gson) > 0:
#         return False
#     if getUrlPlayable.text.replace("\"", "'").startswith("{'detail"):
#         return False
#
#     return {
#             'url': gson[-1]["OriginalTrackUrl"],
#             'cover': "https://resources.tidal.com/images/"+ items[0]["album"]["cover"].replace("-", "/")+ "/640x640.jpg",
#             'id': songID,
#             'title': items[0]['title'],
#             'duration': time_chatting(int(items[0]['duration'])),
#             'artist': items[0]["artist"]["name"],
#             'album': items[0]["album"]["title"]
#             }

class CustomAPI:
    def __init__(self):
        print("API Client Initialized.")

    def search(self, query: str):
        print(f"API: Searching for '{query}'...")
        try:
            req= requests.get(url= api+ "/search/", params= {'s': query})
        except:
            return []
        jsonObj= req.json()
        if not "items" in jsonObj:
            return []
        items= jsonObj["items"]
        res= []
        if len(items) < 1:
            return res
        for item in items:
            print(item)
            shot= {'id': item['id'], 'title': item['title'], 'artist': item['artist']['name'], 'album': item['album']['title'], 'duration': item['duration'], 'cover': "https://resources.tidal.com/images/"+ item["album"]["cover"].replace("-", "/")+ "/640x640.jpg"}
            res.append(shot)
        return res

    def get_track_url(self, track_id: str, quality: str= "LOW", fib= True):
        print(f"API: Getting URL for track_id '{track_id}'...")
        getUrlPlayable= requests.get(url= api+ "/track/", params= {'id': track_id, 'quality': quality})
        gson= getUrlPlayable.json()
        if "error" in gson:
            print('quality not available:', quality)
            if fib:
                get_val= self.get_track_url(track_id, "HIGH", False)
                if get_val== "":
                    get_val= self.get_track_url(track_id, "LOSSLESS", False)
                return get_val
            return ""
        key= 1 if len(gson) == 1 else -1
        if len(gson) < 1:
            return ""
        if not gson or not "OriginalTrackUrl" in gson[key]:
            return ""
        print(gson[key]["OriginalTrackUrl"])
        return gson[key]["OriginalTrackUrl"]

