# -*- coding: UTF-8 -*-
import hashlib
import requests
import shutil

version = "1.4.3"

# print for debugging
def printD(msg):
    print(f"Civitai Helper: {msg}")


def gen_file_sha256(filname):
    printD("Calculate SHA256")
    hash_sha256 = hashlib.sha256()
    with open(filname, "rb") as f:
        # force to use Memory Optimized SHA256
        # In case people don't understand this and uncheck it then stuck their system
        printD("Using Memory Optimized SHA256")
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    hash_value =  hash_sha256.hexdigest()
    printD("sha256: " + hash_value)
    return hash_value


# get preview image
def download_file(url, path):
    printD("Downloading file from: " + url)
    # get file
    r = requests.get(url, stream=True)
    if not r.ok:
        printD("Get error code: " + str(r.status_code))
        printD(r.text)
        return
    
    # write to file
    with open(path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    printD("File downloaded to: " + path)
