"""Group Uniden Scanner Audio by department and format to serve as local podcast using
jekyll.


"""

import sys
import os
from pathlib import Path
import shutil
from sys import argv
from datetime import datetime, date, time, timedelta

from scanner.scanner_utility_functions import get_wav_meta, parse_time
from scanner.constants import PODCAST


# for arg in argv:
#     print(f"arg: {arg}")

destination_path = Path("/Volumes/iMac HDD/uniden-scanner-podcast/scanner_audio/")
podcast_post_path = Path("/Volumes/iMac HDD/uniden-scanner-podcast/_posts/")
# temporary path
source_path = Path("/Volumes/iMac HDD/uniden_scanner_audio/Ch2Alternate/")

wavedata = []

# todo: need to generate the post path
for wave in source_path.iterdir():
    # grab metadata from the wave file
    meta = get_wav_meta(str(wave))

    rec_start = meta["TransmissionStart"]
    rec_end = meta["TransmissionEnd"]

    trans_datetime = parse_time(rec_start, rec_end)

    duration = trans_datetime["PodcastDuration"]

    podcast_string = (
        f"---\n"
        f"title: {1}\n"
        f"date: {trans_datetime['TransmissionStart']['date']}\n"
        f"categories: podcast\n"
        f"tags: {2}\n"
        f"permalink: \n"
        f"podcast_link: {3}"
        f"---"
    )

    print(podcast_string)

    wavedata.append(podcast_string)
