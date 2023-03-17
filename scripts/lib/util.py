# -*- coding: UTF-8 -*-
import os
import io
import hashlib
import requests
import shutil

version = "1.5.6"

def_headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}


# print for debugging
def printD(msg):
    print(f"Civitai Helper: {msg}")


def read_chunks(file, size=io.DEFAULT_BUFFER_SIZE):
    """Yield pieces of data from a file-like object until EOF."""
    while True:
        chunk = file.read(size)
        if not chunk:
            break
        yield chunk

# Now, hashing use the same way as pip's source code.
def gen_file_sha256(filname):
    printD("Use Memory Optimized SHA256")
    blocksize=1 << 20
    h = hashlib.sha256()
    length = 0
    with open(filname, 'rb') as f:
        for block in read_chunks(f, size=blocksize):
            length += len(block)
            h.update(block)

    hash_value =  h.hexdigest()
    printD("sha256: " + hash_value)
    printD("length: " + str(length))
    return hash_value

# def gen_file_sha256(filname):
#     printD("Calculate SHA256")
#     # force to use Memory Optimized SHA256
#     # In case people don't understand this and uncheck it then stuck their system
#     printD("Using Memory Optimized SHA256")
#     hash_sha256 = hashlib.sha256()
#     with open(filname, "rb") as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             hash_sha256.update(chunk)

#     hash_value =  hash_sha256.hexdigest()
#     printD("sha256: " + hash_value)
#     return hash_value


# get preview image
def download_file(url, path):
    printD("Downloading file from: " + url)
    # get file
    r = requests.get(url, stream=True, headers=def_headers)
    if not r.ok:
        printD("Get error code: " + str(r.status_code))
        printD(r.text)
        return
    
    # write to file
    with open(path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    printD("File downloaded to: " + path)

# get subfolder list
def get_subfolders(folder:str) -> list:
    printD("Get subfolder for: " + folder)
    if not folder:
        printD("folder can not be None")
        return
    
    if not os.path.isdir(folder):
        printD("path is not a folder")
        return
    
    prefix_len = len(folder)
    subfolders = []
    for root, dirs, files in os.walk(folder, followlinks=True):
        for dir in dirs:
            full_dir_path = os.path.join(root, dir)
            # get subfolder path from it
            subfolder = full_dir_path[prefix_len:]
            subfolders.append(subfolder)

    return subfolders

