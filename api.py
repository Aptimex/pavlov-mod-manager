import requests
import json
from urllib.request import urlopen

#local files
#from config import apiBase, modPath, PLATFORM, gameID, AUTH_HEADER
from config import *

class Mod:
    name = None
    id = None
    currentVersion = None
    modfile_live = None
    downloadLink = None
    url = None
    downloadSize = None
    extractedSize = None
    md5 = None
    filename = None
    modFolder = None
    
    def __init__(self):
        super(Mod).__init__()
    
    def __str__(self):
        attrs = vars(self)
        return '\n'.join("%s: %s" % item for item in attrs.items())
    
#Pass in the URL path starting with /
def makeAPIRequest(path, headers=API_HEADER):
    #r = requests.get(url, headers=headers)
    r = requests.get(apiBase + path, headers=headers)
    if r.status_code != 200:
        if r.status_code == 429: #Too Many Requests
            wait = int(r.headers["retry-after"]) + 1
            print(f"Rate limit detected, waiting {wait} seconds to continue")
            time.sleep(wait)
            return makeAPIRequest(url, headers)
            
        print(f"Request error, code {r.status_code}")
        #return (None, r.status_code)
    
    return r

def getModfileData(modID, modfile_live):
    #print(f"{modID}_{modfile_live}")
    
    path = f"/games/{gameID}/mods/{modID}/files?id={modfile_live}"
    #r = requests.get(url, headers=header)
    r = makeAPIRequest(path)
    if r.status_code != 200:
        print(f"Error getting mod data for Mod {modID}, modfile {modfile_live}. Code {r.status_code}")
        return None
    #print(json.dumps(r.json(), indent=2))
    
    data = r.json()["data"]
    #print(json.dumps(data, indent=2))
    if len(data) != 1:
        print(f"ERROR: Returned {len(data)} entries for Mod {modID}, modfile {modfile_live}. Expected 1 entry.")
        return None
    
    return data[0]

def getAllModsData(modIDs):
    modList = []
    
    #Process in 100-mod chunks (API limit is 100 results per query)
    for i in range(((len(modIDs)-1) // 100) + 1):
        modBatch = modIDs[i*100:(i+1)*100]
        
        qs = "id-in="
        #for id in modIDs:
        for id in modBatch:
            qs += str(id) + ","
            
        qs = qs[:-1] #remove trailing comma
        
        #Get generic data about the mods
        #Explicitly specify the default limit in case it changes in the future
        endpoint = f"/games/{gameID}/mods/?_limit=100&{qs}"
        
        r = makeAPIRequest(endpoint)
        if r.status_code != 200:
            print(f"Error getting mods info: code {r.status_code}")
            return None
        
        data = r.json()
        
        '''
        with open("A:\\Users\\Adam\\Desktop\\pv.txt", "w") as f:
            f.truncate()
            f.write(json.dumps(data, indent=2))
        '''
        
        for mod in data["data"]:
            modData = Mod()
            modData.name = mod["name"]
            modData.id = mod["id"]
            
            #get current (live) modfile ID for windows platform
            for p in mod["platforms"]:
                if p["platform"].lower() == PLATFORM:
                    modData.modfile_live = p["modfile_live"]
                    break
            if modData.modfile_live == None:
                print(f"Couldn't find '{PLATFORM}' version of mod {modID}, consider unsubscribing/deleting")
                continue
            
            
            # This should be for Windows due to a header we sent
            modfileData = mod["modfile"]
            if modfileData["id"] != modData.modfile_live:
                print(f"ERROR: Returned modfile data is not the one for {PLATFORM}")
                continue
                
            modData.downloadSize = modfileData["filesize"]
            modData.extractedSize = modfileData["filesize_uncompressed"]
            modData.md5 = modfileData["filehash"]["md5"]
            modData.downloadLink = modfileData["download"]["binary_url"]
            modData.url = requests.head(modData.downloadLink, allow_redirects=True).url #resolve to final download URL
            modData.filename = modData.url.split("/")[-1]
            modData.modFolder = "{}\\UGC{}".format(modPath, modData.id)
            
            modList.append(modData)
    
    return modList

#get the latest platform-specific metadata about a mod
#Requires two API requests: One to get generic data (including mod name) and one to get data about the latest version
def getModData(modID, basic=False):
    modData = Mod()
    #modfileData = None
    
    #Get generic data about the mod
    r = makeAPIRequest("/games/{}/mods/{}".format(gameID, modID))
    if r.status_code != 200:
        print("Error getting mod info: code " + str(r.status_code))
        return None
    
    data = r.json()
    modData.name = data["name"] #not available from Modfile Object API
    modData.id = data["id"]
    
    #get current (live) modfile ID for windows platform
    for p in data["platforms"]:
        if p["platform"].lower() == PLATFORM.lower():
            modData.modfile_live = p["modfile_live"]
            break
    if modData.modfile_live == None:
        print("Couldn't find '{}' version of mod {}, consider unsubscribing/deleting".format(PLATFORM.lower(), modID))
        return None
    
    if basic:
        return modData
    
    modfileData = getModfileData(modID, modData.modfile_live)
    if not modfileData:
        print("Unable to obtain mod's most recent data")
        return None
    
    modData.downloadSize = modfileData["filesize"]
    modData.extractedSize = modfileData["filesize_uncompressed"]
    modData.md5 = modfileData["filehash"]["md5"]
    modData.downloadLink = modfileData["download"]["binary_url"]
    modData.url = urlopen(modData.downloadLink).url #resolve to final download URL
    modData.filename = modData.url.split("/")[-1]
    modData.modFolder = "{}\\UGC{}".format(modPath, modID)
    
    return modData
