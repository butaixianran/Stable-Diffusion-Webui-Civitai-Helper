# -*- coding: UTF-8 -*-
import os
import io
import hashlib
import requests
import shutil


version = "1.8.1"

def_headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}


proxies = None


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
    with open(os.path.realpath(filname), 'rb') as f:
        for block in read_chunks(f, size=blocksize):
            length += len(block)
            h.update(block)

    hash_value =  h.hexdigest()
    printD("sha256: " + hash_value)
    printD("length: " + str(length))
    return hash_value



# get preview image
def download_file(url, path):
    printD("Downloading file from: " + url)
    # get file
    r = requests.get(url, stream=True, headers=def_headers, proxies=proxies)
    if not r.ok:
        printD("Get error code: " + str(r.status_code))
        printD(r.text)
        return
    
    # write to file
    with open(os.path.realpath(path), 'wb') as f:
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


# get relative path
def get_relative_path(item_path:str, parent_path:str) -> str:
    # printD("item_path:"+item_path)
    # printD("parent_path:"+parent_path)
    # item path must start with parent_path
    if not item_path:
        return ""
    if not parent_path:
        return ""
    if not item_path.startswith(parent_path):
        return item_path

    relative = item_path[len(parent_path):]
    if relative[:1] == "/" or relative[:1] == "\\":
        relative = relative[1:]

    # printD("relative:"+relative)
    return relative