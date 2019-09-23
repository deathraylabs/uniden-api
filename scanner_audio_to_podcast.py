"""Group Uniden Scanner Audio by department and format to serve as local podcast using
jekyll.


"""

import sys
import os
from pathlib import Path
import shutil
from sys import argv

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

    file_date = f"{rec_time[:4]}-{rec_time[4:6]}-{rec_time[6:8]}"

    podcast_string = (
        f"---\n"
        f"title: {1}\n"
        f"date: {file_date}\n"
        f"categories: podcast\n"
        f"tags: {2}\n"
        f"permalink: \n"
        f"podcast_link: {3}"
    )

    print(podcast_string)

    wavedata.append(podcast_string)
