# -*- coding: UTF-8 -*-
import sys
import requests
import os
from . import util


dl_ext = ".downloading"

# disable ssl warning info
requests.packages.urllib3.disable_warnings()

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
    rh = requests.get(url, stream=True, verify=False, headers=util.def_headers)
    # get file size
    total_size = 0
    total_size = int(rh.headers['Content-Length'])
    util.printD(f"File size: {total_size}")

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

    # use a temp file for downloading
    base, ext = os.path.splitext(file_path)
    dl_file_path = base+dl_ext


    util.printD(f"Downloading to temp file: {dl_file_path}")

    # check if downloading file is exsited
    downloaded_size = 0
    if os.path.exists(dl_file_path):
        downloaded_size = os.path.getsize(dl_file_path)

    util.printD(f"Downloaded size: {downloaded_size}")

    # create header range
    headers = {'Range': 'bytes=%d-' % downloaded_size}
    headers['User-Agent'] = util.def_headers['User-Agent']

    # download with header
    r = requests.get(url, stream=True, verify=False, headers=headers)

    # write to file
    with open(dl_file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                downloaded_size += len(chunk)
                f.write(chunk)
                # force to write to disk
                f.flush()

                # progress
                progress = int(50 * downloaded_size / total_size)
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stdout.write("\r[%s%s] %d%%" % ('-' * progress, ' ' * (50 - progress), 100 * downloaded_size / total_size))
                sys.stdout.flush()

    print()

    # rename file
    os.rename(dl_file_path, file_path)
    util.printD(f"File Downloaded to: {file_path}")
    return file_path

