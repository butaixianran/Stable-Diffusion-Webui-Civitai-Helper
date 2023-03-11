# -*- coding: UTF-8 -*-
import sys
import requests
import os
import util


dl_ext = ".downloading"

# disable ssl warning info
requests.packages.urllib3.disable_warnings()

def download(url, file_path, size):
    # use a temp file for downloading
    base, ext = os.path.splitext(file_path)
    dl_file_path = os.path.join(base, dl_ext)

    total_size = 0
    if size:
        total_size = size
    else:
        # get file size
        rhead = requests.get(url, stream=True, verify=False)
        total_size = int(rhead.headers['Content-Length'])

    util.printD(f"File size: {total_size}")

    util.printD(f"Downloading to temp file: {dl_file_path}")

    # check if downloading file is exsited
    downloaded_size = 0
    if os.path.exists(dl_file_path):
        downloaded_size = os.path.getsize(dl_file_path)

    util.printD(f"Downloaded size: {downloaded_size}")

    # get header range
    headers = {'Range': 'bytes=%d-' % downloaded_size}
    # download with header
    r = requests.get(url, stream=True, verify=False, headers=headers)

    # write to file
    with open(file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                downloaded_size += len(chunk)
                f.write(chunk)
                # force to write to disk
                f.flush()

                # progress
                progress = int(50 * downloaded_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('█' * progress, ' ' * (50 - progress), 100 * downloaded_size / total_size))
                sys.stdout.flush()

    print()

    # rename file
    os.rename(dl_file_path, file_path)
    util.printD(f"File Downloaded to: {file_path}")

