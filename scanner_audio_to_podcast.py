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
    meta = get_wav_meta(str(wave))
    wavedata.append(meta)
