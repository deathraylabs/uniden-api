"""Group Uniden Scanner Audio by department and format to serve as local podcast using
jekyll.

Source wav files will be copied over to the podcast directory.

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
podcast_post_base_path = Path("/Volumes/iMac HDD/uniden-scanner-podcast/_posts/")

# path to directory that contains the directories with audio you add
source_path_root = Path("/Volumes/iMac HDD/uniden-scanner-podcast/_site/scanner_audio/")

# name of directory that contains audio of interest
audio_directory = "Ch2Alternate"

source_path = source_path_root.joinpath(audio_directory)

if not source_path.is_dir():
    raise NotADirectoryError

wavedata = []

for wave in source_path.iterdir():
    # grab metadata from the wave file
    meta = get_wav_meta(str(wave))

    rec_start = meta["TransmissionStart"]
    rec_end = meta["TransmissionEnd"]

    # function provides separate "time" and "date" objects for start and end
    trans_datetime = parse_time(rec_start, rec_end)

    duration = trans_datetime["PodcastDuration"]
    start_date = trans_datetime["TransmissionStart"]["date"]
    start_time = trans_datetime["TransmissionStart"]["time"].replace(":", "-")

    # get the channel name (aka TGID name)
    tgid_name = meta["TGID:Name"]

    # replace characters that must be escaped in HTML
    tgid_name = tgid_name.replace(".", "")
    tgid_name = tgid_name.replace(" ", "-")

    # podcast post name needs to include date, title, and time
    post_name = f"{start_date}_{start_time}-{tgid_name}.md"

    podcast_post_path = podcast_post_base_path.joinpath(post_name)

    podcast_string = (
        f"---\n"
        f"title: {rec_start + '_' + tgid_name}\n"
        f"date: {trans_datetime['TransmissionStart']['date']}\n"
        f"categories: podcast\n"
        f"tags: \n"
        f"permalink: \n"
        f"podcast_link: http://localhost:4000/scanner_audio/{audio_directory}/{wave.name}\n"
        f"---"
    )

    # save as markdown file to podcast posts
    with open(podcast_post_path, "w") as f:
        f.write(podcast_string)

    print(podcast_string)

    # wavedata.append(podcast_string)
