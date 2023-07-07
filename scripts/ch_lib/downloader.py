# -*- coding: UTF-8 -*-
import sys
import requests
import os
from . import util


dl_ext = ".downloading"

# disable ssl warning info
requests.packages.urllib3.disable_warnings()

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

# output is downloaded file path
def dl(url, folder, filename, filepath):
    util.printD("Start downloading from: " + url)
    # get file_path
    file_path = ""
    if filepath:
        file_path = filepath
    else:
        # if file_path is not in parameter, then folder must be in parameter
        if not folder:
            util.printD("folder is none")
            return
        
        if not os.path.isdir(folder):
            util.printD("folder does not exist: "+folder)
            return
        
        if filename:
            file_path = os.path.join(folder, filename)

    # first request for header
    rh = requests.get(url, stream=True, verify=False, headers=util.def_headers, proxies=util.proxies)
    # get file size
    total_size = 0
    total_size = int(rh.headers['Content-Length'])
    util.printD(f"File size: {human_readable_size(total_size)}")

    # if file_path is empty, need to get file name from download url's header
    if not file_path:
        filename = ""
        if "Content-Disposition" in rh.headers.keys():
            cd = rh.headers["Content-Disposition"]
            # Extract the filename from the header
            # content of a CD: "attachment;filename=FileName.txt"
            # in case "" is in CD filename's start and end, need to strip them out
            filename = cd.split("=")[1].strip('"')
            if not filename:
                util.printD("Fail to get file name from Content-Disposition: " + cd)
                return
            
        if not filename:
            util.printD("Can not get file name from download url's header")
            return
        
        # with folder and filename, now we have the full file path
        file_path = os.path.join(folder, filename)


    util.printD("Target file path: " + file_path)
    base, ext = os.path.splitext(file_path)

    # check if file is already exist
    count = 2
    new_base = base
    while os.path.isfile(file_path):
        util.printD("Target file'" + file_path + "'already exist.")
        # re-name
        new_base = base + "_" + str(count)
        file_path = new_base + ext
        count += 1

    # use a temp file for downloading
    dl_file_path = new_base+dl_ext


    util.printD(f"Downloading to temp file: {dl_file_path}")

    # check if downloading file is exsited
    downloaded_size = 0
    if os.path.exists(dl_file_path):
        downloaded_size = os.path.getsize(dl_file_path)
        if downloaded_size > 0:
            util.printD(f"Downloaded size: {downloaded_size}")

    # create header range
    headers = {'Range': 'bytes=%d-' % downloaded_size}
    headers['User-Agent'] = util.def_headers['User-Agent']

    # download with header
    r = requests.get(url, stream=True, verify=False, headers=headers, proxies=util.proxies)

    # write to file
    with open(dl_file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                downloaded_size += len(chunk)
                f.write(chunk)
                # force to write to disk
                f.flush()

                # progress
                progress = int(100 * downloaded_size / total_size)
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stdout.write("\r[%s%s] %d%%" % ('=' * progress, ' ' * (100 - progress), 100 * downloaded_size / total_size))
                sys.stdout.flush()

    print()

    # rename file
    os.rename(dl_file_path, file_path)
    util.printD(f"File save to: {file_path}")
    return file_path

