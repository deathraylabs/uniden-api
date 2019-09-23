"""Group Uniden Scanner Audio by department and format to serve as local podcast using
jekyll.


"""

import sys
import os
from pathlib import Path
import shutil
from sys import argv
from datetime import datetime, date, time, timedelta

from scanner.scanner_utility_functions import get_wav_meta
from scanner.constants import PODCAST


# for arg in argv:
#     print(f"arg: {arg}")

destination_path = Path("/Volumes/iMac HDD/uniden-scanner-podcast/scanner_audio/")
podcast_post_path = Path("/Volumes/iMac HDD/uniden-scanner-podcast/_posts/")
# temporary path
source_path = Path("/Volumes/iMac HDD/uniden_scanner_audio/Ch2Alternate/")

wavedata = []

# todo: need to match get_wav_metadata to dict style used while reading scanner
for wave in source_path.iterdir():
    # grab metadata from the wave file
    meta = get_wav_meta(str(wave))

    rec_time = meta["TransmissionStart"]

    # time and date that the recording started
    trans_start_date = date(int(rec_time[:4]), int(rec_time[4:6]), int(rec_time[6:8]))
    trans_start_time = time(
        int(rec_time[8:10]), int(rec_time[10:12]), int(rec_time[12:])
    )

    podcast_string = (
        f"---\n"
        f"title: {1}\n"
        f"date: {trans_start_date}\n"
        f"categories: podcast\n"
        f"tags: {2}\n"
        f"permalink: \n"
        f"podcast_link: {3}"
        f"---"
    )

    print(podcast_string)

    wavedata.append(podcast_string)
