"""Group Uniden Scanner Audio by department and format to serve as local podcast using
jekyll.


"""

import sys
import os
from pathlib import Path
import shutil
from sys import argv

from scanner.scanner_utility_functions import get_wav_meta


# for arg in argv:
#     print(f"arg: {arg}")

destination_path = Path("/Volumes/iMac HDD/uniden-scanner-podcast/scanner_audio/")
# temporary path
source_path = Path("/Volumes/iMac HDD/uniden_scanner_audio/Ch2Alternate/")

meta = get_wav_meta(source_path)
