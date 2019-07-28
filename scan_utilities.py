"""
Utility functions for use with Uniden SDS-100 and uniden-api code.
"""

from pydub import AudioSegment
from pathlib import Path

# import shutil
# import sys
import os
import subprocess as sb
import pyperclip as cb
import re
import chunk
import pandas as pd


def unique_path(directory, name_pattern):
    """Create a new and unique file name.

    Args:
        directory (Path): pathlib object representing containing directory
        name_pattern (str): str.format pattern of desired file name

    Returns:
        Path: unique pathlib object based on naming scheme

    Example:
        Create a unique path object using str.format patterns like this::

            path = unique_path(pathlib.Path.cwd(), "test{:03d}.txt")

    """
    counter = 0
    while True:
        counter += 1
        path = directory / name_pattern.format(counter)
        if not path.exists():
            return path


def files_with_matched_tags(working_dir, tags):
    """Function generates a list of files with matching extended
    attribute tags in the finder.

    Args:
        working_dir (str): directory containing tagged files, spaces do not
            need to be escaped, file name will be stripped.
        tags (str): string containing one or more comma-separated finder
            tags you wish to match against

    Returns:
        list: list of Path objects for files that match the specified finder
              tags
        None: returned if no files match specified finder tag

    """

    # The tag command can be found at https://github.com/jdberry/tag
    # tagCmd is location of tag executable on computer
    tagCmd = Path("/usr/local/bin/tag")

    # strip the file name to ensure we're working with directory only
    working_dir = Path(working_dir).parent

    # change the current working directory to the location of audio files
    os.chdir(working_dir)

    # capture_output=True ensures we capture byte string of the resultant stdout
    tag_string = sb.run([str(tagCmd), "--match", tags], capture_output=True).stdout

    # check for case of no matching tags
    if tag_string == b"":
        print("No files with matching tags.")
        return None

    # convert stdout into usable list of file names that match
    tag_string = tag_string.decode()  # decode bytestring back to utf-8
    tag_string = tag_string.strip()  # strip off last newline character
    tagged_files = list(tag_string.split("\n"))
    tagged_files.sort()  # ensure files are in ascending order

    # takes the list of file names and creates a list of absolute paths
    paths_to_tagged_files = [working_dir / path for path in tagged_files]

    return paths_to_tagged_files


def merge_tagged_wav_files(wav_file_paths, merged_wav_name=r"merged_{:03d}.wav"):
    """ Simple function to combine multiple wav files into a single file.

    Args:
        wav_file_paths (list): list of Path objects for wav files you wish to
            combine
        merged_wav_name (str): optional file name and format string.

    Returns:
        False (bool): if no wave files are passed to the function
        (str): string containing path to newly created wav file

    """
    if wav_file_paths is None:
        print("No files contained specified tags.")
        return False

    # container for wav files we wish to be merged
    combined_sounds = AudioSegment.empty()

    # create our Path object
    # merged_wav_name = Path(merged_wav_name)

    # don't overwrite existing files
    merged_wav_path = unique_path(Path.cwd(), merged_wav_name)

    for file in wav_file_paths:
        combined_sounds = combined_sounds + AudioSegment.from_wav(str(file))

    combined_sounds.export(merged_wav_path, format="wav")

    return merged_wav_path


def get_wav_meta(directory):
    """Read the scanner generated metadata at the start of the file

    Args:
        directory (str): location of wav file

    """
    scan_frame = pd.DataFrame(columns=["offset", "data"])

    f_path = Path(directory)
    f = open(f_path, "rb")

    # chunk will allow us to parse the byte data in the wav file
    meta_chunk = chunk.Chunk(f)

    # variable to keep track of location in byte stream
    current_byte = 0
    raw_string = "\x00"
    row_dict = {"offset": 0, "data": ""}

    while current_byte < 2663:
        # print(f"the current byte is: {current_byte}")

        try:
            chunk_string = meta_chunk.read(1).decode()
        except UnicodeDecodeError:
            print("just hit a weird byte chunk")
            # current_byte = meta_chunk.tell() + 8  # first 8 don't count
            # raw_string += f"\n-=-=-=-= byte {current_byte} =-=-=-=-=-\n"
            raw_string += f"[~{current_byte}]\n"
            continue
        finally:
            current_byte = meta_chunk.tell() + 8  # first 8 don't count

        # todo: the offset is not being recorded correctly in dataframe
        # skip null bytes before first character
        if chunk_string == "\x00" and row_dict["data"] == "":
            raw_string += chunk_string
            continue
        # save data to frame once we hit the next null character
        elif chunk_string == "\x00" and row_dict["data"] != "":
            print(row_dict)
            # populate the pandas dataframe
            scan_frame = scan_frame.append(row_dict, ignore_index=True)
            # reset the data in dict
            row_dict["data"] = ""
        elif raw_string[-1] == "\x00" and chunk_string != "\x00":
            raw_string += f"[{current_byte}]" + chunk_string
            row_dict["offset"] = current_byte
            row_dict["data"] = row_dict["data"] + chunk_string
        else:
            raw_string += chunk_string
            row_dict["data"] = row_dict["data"] + chunk_string

        current_byte = meta_chunk.tell() + 8
        # print(f"The ending byte was: {current_byte}")

    f.close()

    return raw_string, scan_frame


if __name__ == "__main__":

    help_statement = """
        **********************
        Copy path to directory
        Then hit "Enter"
        ----------------------
    """

    # input(help_statement)
    #
    # # get contents of clipboard
    # clipboard = cb.paste()
    #
    # # path to directory that contains the audio of interest
    # # wav_dir_path = "/Users/peej/Downloads/uniden audio/01 HPD-N/2019-07-17_09-50-28.wav"
    #
    # # matching tag
    # tag = "Orange"
    # output_file_name = "code pit.wav"
    #
    # matched_files = files_with_matched_tags(clipboard, tag)
    # output = merge_tagged_wav_files(matched_files)

    # todo: reset the tag to something else after it's merged

    audio_path = "/Users/peej/Downloads/uniden audio/00 HPD-NW/2019-07-05_11-39-47.wav"

    metadata = get_wav_meta(audio_path)
    metalist = re.sub(r"(?:\x00+)", "\n", metadata[0])
