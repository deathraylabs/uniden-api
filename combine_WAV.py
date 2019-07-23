"""
Merge two or more WAV files together, specifically from Uniden SDS-100 scanner.

Usage: 
    combine_WAV.py FolderName

dir    : directory containing audio files and marker tag

"""

from pydub import AudioSegment
from pathlib import Path

# import shutil
# import sys
import os
import subprocess as sb


def files_with_matched_tags(working_dir, tags):
    """Function that generates a list of files with matching extended
    attribute tags in the finder.

    Args:
        working_dir (str): directory containing tagged files, spaces do not
            need to be escaped.
        tags (str): one or more finder tags you want to match against

    Returns:
        list: list of absolute paths to files that match the specified finder
            tags
        None: returned if no files match specified finder tag

    """

    # The tag command can be found at https://github.com/jdberry/tag
    # tagCmd is location of tag executable on computer
    tagCmd = "/usr/local/bin/tag"

    # change the current working directory to the location of audio files
    os.chdir(working_dir)

    # capture_output=True ensures we capture byte string of the resultant stdout
    tag_string = sb.run([tagCmd, "--match", tags], capture_output=True).stdout

    # check for case of no matching tags
    if tag_string == b"":
        print("No files with matching tags.")
        return None

    # convert stdout into usable list of file names that match
    tag_string = tag_string.decode()  # decode bytestring back to utf-8
    tag_string = tag_string.strip()  # strip off last newline character
    tagged_files = list(tag_string.split("\n"))

    # takes the list of file names and creates a list of absolute paths
    paths_to_tagged_files = [os.path.join(working_dir, path) for path in tagged_files]

    return paths_to_tagged_files


def merge_tagged_wav_files(wav_file_paths, output_path="test_file.wav"):
    """ Simple function to combine multiple wav files into a single file.

    Args:
        wav_file_paths (list): list of paths to wav files you wish to combine
        output_path (str): optional file name and path.
            - individual file names will be saved into CWD
            - specify full path name to save in a specific directory
            - existing files of the same name will be overwritten

    Returns:
        False (bool): if no wave files are passed to the function
        (str): string containing path to newly created wav file

    """
    # container for wav files we wish to be merged
    combined_sounds = AudioSegment.empty()

    if wav_file_paths is None:
        print("No files contained specified tags.")
        return False

    for file in wav_file_paths:
        combined_sounds += AudioSegment.from_wav(str(file))

    combined_sounds.export(output_path, format="wav")

    return output_path


if __name__ == "__main__":
    # path to directory that contains the audio of interest
    wav_dir_path = "/Users/peej/Downloads/uniden audio/01 HPD-N/"

    # matching tag
    tag = "red"

    matched_files = files_with_matched_tags(wav_dir_path, tag)
    output = merge_tagged_wav_files(matched_files)

    # todo: reset the tag to something else after it's merged
