"""Create a local podcast feed from a directory containing individual wave files.

Notes:
    1. Requires Jekyll server in order to serve the podcast to itunes.
    2. Steps to setup jekyll server using terminal:
        a. `cd /Volumes/iMac HDD/uniden-scanner-podcast/`
        b. `bundle exec jekyll serve`
    3. Use the following symlink as directory for adding wav files to podcast:
        `/Volumes/iMac HDD/scanner_audio/`


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

# jekyll server href base path to scanner files
href_base = "http://localhost:4000/scanner_audio/"


destination_path = Path("/Volumes/iMac HDD/uniden-scanner-podcast/scanner_audio/")
podcast_post_base_path = Path("/Volumes/iMac HDD/uniden-scanner-podcast/_posts/")

# path to directory that contains the directories with audio to be served
source_path_root = Path("/Volumes/iMac HDD/scanner_audio/")

# name of directory that contains audio of interest
audio_directory = "0_HPD-NW"

source_path = source_path_root.joinpath(audio_directory)

if not source_path.is_dir():
    raise NotADirectoryError

wavedata = []

# get the path for each wave file in the directory
for wave in source_path.iterdir():

    # wav file size and conversion
    wav_file_size = os.path.getsize(wave)
    wav_size = f"{wav_file_size // 1000} KB"  # converts bytes to KB

    # location of audio file on jekyll web server
    wav_href = f"{href_base}{audio_directory}/{wave.name}"

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
    # there must be hyphens between the date items and title or it breaks
    post_name = f"{start_date}-{start_time}-{tgid_name}.md"

    podcast_post_path = podcast_post_base_path.joinpath(post_name)

    # todo: get the file size
    podcast_string = (
        f"---\n"
        f"layout: post\n"
        f"title: \"{rec_start + '_' + tgid_name}\"\n"
        f"date: {trans_datetime['TransmissionStart']['date']}\n"
        f"categories: podcast\n"
        f"tags: \n"
        f"permalink: /podcasts/{audio_directory}-{wave.stem}\n"
        f"podcast_link: http://localhost:4000/scanner_audio/{audio_directory}/{wave.name}\n"
        f"podcast_file_size: {wav_size}\n"
        f'podcast_duration: "{str(duration)}"\n'
        f"podcast_length: {meta['FileSize']}\n"
        f"---\n\n"
        f"{post_name}"
    )

    # save as markdown file to podcast posts
    with open(podcast_post_path, "w") as f:
        f.write(podcast_string)

    # print(podcast_string)

    # wavedata.append(podcast_string)
