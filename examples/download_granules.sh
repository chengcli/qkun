#! /bin/bash
search-granule pace OCI-L1B --start 2025-03-26 --end 2025-03-27 --bbox -10 30 10 50 --quiet > download_list.txt
download-granule download_list.txt --select ::2 --save-dir ${HOME}/.cache/qkun
