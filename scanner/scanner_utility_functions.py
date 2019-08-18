"""
Utility functions for use with Uniden SDS-100 and uniden-api code.
"""


from pathlib import Path
import os
import subprocess as sb
import shutil
import pyperclip as cb

from collections import OrderedDict
from tinytag import TinyTag
import chunk

from pydub import AudioSegment
from scanner.constants import *

# import pandas as pd


def unique_path(directory, name_pattern):
    """Create a new and unique file name.

    Args:
        directory (Path): pathlib object representing containing wav_source
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


def get_directories(directory):
    """Return all directories contained within the passed wav_source. Doesn't
    scan recursively for subdirectories.

    Args:
        directory (str): path string to container wav_source

    Returns:
        list: list of all directories found as Path objects
    """
    # create path object
    dir = Path(directory)
    directories = []

    # check to ensure function was passed an actual path
    if not (dir.is_file() or dir.is_dir()):
        return None

    # strip the file name to ensure we're working with wav_source only
    if dir.is_file():
        dir = dir.parent

    for item in dir.iterdir():
        if item.is_dir():
            directories.append(item)

    return directories


def files_with_matched_tags(working_dir, tags):
    """Function generates a list of files with matching extended
    attribute tags in the finder.

    Args:
        working_dir (str): wav_source containing tagged files, spaces do not
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

    # create path object
    working_dir = Path(working_dir)

    # check to ensure function was passed an actual path
    if not (working_dir.is_file() or working_dir.is_dir()):
        return None

    # strip the file name to ensure we're working with wav_source only
    if working_dir.is_file():
        working_dir = working_dir.parent

    # change the current working wav_source to the location of audio files
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

    # don't overwrite existing files
    merged_wav_path = unique_path(Path.cwd(), merged_wav_name)

    for file in wav_file_paths:
        combined_sounds = combined_sounds + AudioSegment.from_wav(str(file))

    combined_sounds.export(merged_wav_path, format="wav")

    return merged_wav_path


def get_wav_meta(wav_source, chunk_dict={}):
    """Read the scanner generated metadata at the start of the file

    Args:
        wav_source (str or Chunk): path string of wav file

    Returns:
        (dict): RIFF tag name: string or bytes representing tag data

    Notes:
        It looks like the scanner is only saving the first 64 bytes of data
        from any given formatting category, then space, then another 64 bytes.

    """
    # scan_frame = pd.DataFrame(columns=["offset", "data"])

    # if the wav_source is not already a Chunk instance, treat it like file
    if not isinstance(wav_source, chunk.Chunk):
        f_path = Path(wav_source)
        f = open(f_path, "rb")

        # The file name is the transmission start time, reformatting to match the
        # transmission end time found in the WAV header.
        transmission_start = f_path.stem.replace("-", "")
        transmission_start = transmission_start.replace("_", "")

        # initializing dict containing chunk data
        chunk_dict = {"transmission_start": transmission_start}

        # chunk will allow us to parse the byte data in the wav file
        meta_chunk = chunk.Chunk(f, align=False, bigendian=False, inclheader=False)
    else:
        try:
            meta_chunk = chunk.Chunk(
                wav_source, align=False, bigendian=False, inclheader=False
            )
        except OSError:
            print("no more chunks!")

    # meta_chunk_name = meta_chunk.getname()
    # meta_chunk_size = meta_chunk.getsize()

    # the first 4 bytes are the first chunk ID and should be "WAVE"
    try:
        if meta_chunk.getname() == b"RIFF":
            try:
                first_id = meta_chunk.read(4)
                if first_id != b"WAVE":
                    print("First tag ID is not WAVE")
                    return
            except AssertionError:
                print("This is not a standard WAVE file.")
                return

            # create a new instance that is the child to RIFF chunk
            # meta_chunk = get_wav_meta(meta_chunk, chunk_dict)
            return get_wav_meta(meta_chunk, chunk_dict)

    except AssertionError:
        print("The file is malformed.")
        return

    chunk_id = meta_chunk.getname()
    chunk_length = meta_chunk.getsize()
    current_location = meta_chunk.tell()

    if chunk_id == b"LIST":
        if current_location == 0:
            list_chunk = meta_chunk.read(4)
            if list_chunk == b"INFO":
                print("Info chunk")
                return get_wav_meta(wav_source, chunk_dict)
            else:
                print("no info chunk")
                return
        elif current_location == chunk_length:
            # meta_chunk.close()
            return get_wav_meta(meta_chunk, chunk_dict)
            # return

    if chunk_id == b"fmt ":
        print("We've reached the end of the header metadata.")
        # don't return the chunk dict if it's just that first entry.
        if len(chunk_dict.items()) <= 1:
            return
        else:
            return chunk_dict

    # todo: build out this logic
    if chunk_id == b"unid":
        print(chunk_length)
        return get_wav_meta(meta_chunk, chunk_dict)

    uniden_chunk_id = WAV_METADATA[chunk_id.decode()]
    chunk_dict[uniden_chunk_id] = meta_chunk.read().decode()

    # meta_chunk.close()
    return get_wav_meta(wav_source, chunk_dict)
    # return

    # this tells us the overall size of the header in bytes
    chunk_length = meta_chunk.read(4)

    # converts byte data to an integer we can work with
    chunk_length = int.from_bytes(chunk_length, byteorder="little")

    chunk_dict["WAVELIST"] = chunk_length

    # The byte offset here is just approximate
    # todo: use a better conditional for while loop
    while meta_chunk.tell() < 925:
        # get chunk name and chunk length
        chunk_name = meta_chunk.read(4)  # this also sets new absolute seek pos
        # decode chunk name to UTF-8
        chunk_name = chunk_name.decode()

        # the very first chunk is the "INFO"
        if chunk_name == "INFO":
            # INFO is zero length, IART begins right after it.
            continue

        # next 4 bytes are little endian order hex number, not ASCII code
        chunk_length = meta_chunk.read(4)
        chunk_length = int.from_bytes(chunk_length, byteorder="little")

        # -------------Uniden proprietary chunk----------------- #

        if chunk_name == "unid":
            # unid is 2048 bytes long but only first 328 bytes are utf8
            # I don't understand code starting after byte 1180 or so
            # chunk_string = meta_chunk.read(chunk_length)

            # absolute starting byte position of current chunk
            start_byte = meta_chunk.tell()

            delimited_lines_bytes = []
            # variable to contain decoded string
            delimited_lines = []

            # record all UTF-8 bytes and stop at the first non-UTF-8 byte
            while meta_chunk.tell() - start_byte <= chunk_length:
                # scanner records 64 bytes of format, then adds null separator
                chunk_line_bytes = meta_chunk.read(65)
                try:
                    chunk_line = chunk_line_bytes.decode()
                # hop out of the loop once you hit a non-utf8 character
                except UnicodeDecodeError as e:
                    pos_in_chunk = meta_chunk.tell() - start_byte
                    # todo: change to logging instead of printing
                    # print(
                    #     f"{e}"
                    #     f"position in chunk: {pos_in_chunk}\nabsolute "
                    #     f"position: {meta_chunk.tell()}"
                    # )
                    break

                chunk_line = chunk_line.rstrip("\x00")
                chunk_line = chunk_line.replace("\x00", "\t")
                chunk_line = chunk_line.split("\t")

                delimited_lines_bytes.append(chunk_line_bytes)
                delimited_lines.append(chunk_line)

                # create new entry in dict for raw lines (for debugging)
                chunk_dict[f"line {len(delimited_lines)}"] = chunk_line

            # todo: ensure lines go to correct definition list
            data_heading_sources = (
                UNID_FAVORITES_DATA,
                UNID_SYSTEM_DATA,
                UNID_DEPARTMENT_DATA,
                UNID_CHANNEL_DATA,
                UNID_SITE_DATA,
                UNID_UNITID_DATA,
                UNID_CONVENTIONAL_DATA,
            )

            # storage for unid data
            unid_list = []

            # creates a list of all the items from unid header
            for index, line in enumerate(data_heading_sources):
                unid_list += list(zip(line, delimited_lines[index]))

            # need to save to dict because second half requires it's own save
            # chunk_dict["unid:Delimited"] = unid_list

            # grab key and value from each tuple and save to dict
            for meta_item in unid_list:
                chunk_dict[meta_item[0]] = meta_item[1]

            continue

        # IKEY is not UTF8, not sure what it is
        elif chunk_name == "IKEY":
            chunk_string = meta_chunk.read(chunk_length)
        else:
            # get the data in the next `chunk_length` bytes
            chunk_string = meta_chunk.read(chunk_length)

            chunk_string = chunk_string.rstrip(b"\x00")

            chunk_string = chunk_string.decode()

            # the file spec uses tab separated values but the datastream
            # from scanner seems to just use null bytes
            chunk_string = chunk_string.replace("\x00", "\t")

        # try to get the actual descriptive name from the chunk name
        try:
            chunk_key = WAV_METADATA[chunk_name]
        except KeyError:
            chunk_key = chunk_name

        # save data to dict
        chunk_dict[chunk_key] = chunk_string

        # debugging text
        # print(f"name: {chunk_name}\nlength: {chunk_length}")
        # print(f"string:\n{chunk_string}")
        # print(f"ending byte no: {meta_chunk.tell()}\n")

    f.close()

    return chunk_dict


def get_string_at_offset(start, length, directory):
    """Grab data from start offset to ending offset

    Args:
        start (int): starting offset byte from start of file (as you see
            using hex editor.
        length (int): number of bytes of data to retreive

    Returns:
        (str): UTF-8 decoded string from bytes

    Notes:
        Here's what I've figured out so far:

        Apparently the WAV header is in little endian byte order. I don't
        know if it is algined every 2 bytes, which is one of the default
        arguments in the `chunk` module.

        the first 8 bytes tell you the chunk name, then the following 4 bytes
        is a little endian hex representation of the chunk size in bytes.

    """
    f_path = Path(directory)
    f = open(f_path, "rb")

    # chunk will allow us to parse the byte data in the wav file
    meta_chunk = chunk.Chunk(f, align=False, bigendian=False, inclheader=True)

    # seek ignores first 8 bytes of file that hex editor sees.
    seek_start_position = start - 8

    # seek to starting byte (seek(0) is actually byte 8 of file)
    meta_chunk.seek(seek_start_position)

    decoded_string = ""

    # read byte by byte to avoid non-ascii characters
    while length > 0:
        chunk_string = meta_chunk.read(1)
        # weird character codes that show up in the string, converted so I
        # can read them in the string output as utf8 text
        chunk_string = chunk_string.replace(b"\x00", b"|")  # NUL
        chunk_string = chunk_string.replace(b"\x01", b"\\x01")  # SOH
        chunk_string = chunk_string.replace(b"\x02", b"\\x02")  # STX
        chunk_string = chunk_string.replace(b"\x03", b"\\x03")  # ETX
        chunk_string = chunk_string.replace(b"\x04", b"\\x04")  # EOT
        chunk_string = chunk_string.replace(b"\x08", b"\\x08")  # BS

        current_pos = meta_chunk.tell()

        try:
            decoded_string += chunk_string.decode()
        except UnicodeDecodeError:
            print(f"shittle sticks at {current_pos} hex: {chunk_string}")
            # label undecodable spots with position and raw hex
            decoded_string += f"«{current_pos} {chunk_string}»"
        finally:
            length -= 1

    # replace null character with nothing
    # chunk_string = chunk_string.replace("\x00", "")

    f.close()

    return decoded_string


def group_audio_by_department(directory="~/Downloads/uniden audio/"):
    """Function takes directories as exported from scanner and groups the
    audio recordings into new directories based on department name.
    """

    # Path object for the root of our folder tree
    basepath = Path(directory).expanduser()

    # todo: change logic to use pathlib instead of shutil
    for folder in basepath.iterdir():
        if folder.is_dir():
            # the .glob ensures that we only get audio files, no hidden files
            for file in folder.glob("*.wav"):
                # create tinytag object that contains metadata
                ttag = TinyTag.get(file)
                # get the department name, which is stored under title
                department = ttag.title
                # forward slashes are not allowed in path names,
                # this will convert them to space instead
                try:
                    department = department.replace("/", " ")
                except AttributeError:
                    print("Encountered file without department tag.")
                    break

                # create new folders for each department if it doesn't alread exist
                p = Path(basepath, department)
                if not p.exists():
                    p.mkdir(exist_ok=True)  # wont overwrite existing wav_source
                    print("New folder created for {}.".format(str(department)))

                # move individual .wav files to their respective dept folders
                try:
                    shutil.move(str(file), str(p))
                except:
                    #                 print("{} already exists".format(str(p)))
                    pass

    # remove the directories that are now empty
    for folder in basepath.iterdir():
        try:
            folder.rmdir()
            print("{} deleted".format(str(folder)))
        except:
            #         print("Directory '{}' isn't empty".format(str(folder)))
            pass

    return


# todo: add test functions
def convert_dir_name(directory):
    """Utility function to convert hexadecimal encoded wav_source string into
    standard decimal format.

    Args:
        directory (str): 4 byte hex number wav_source name

    Returns:
        str: yyyy-MM-DD_hh_mm_ss
    """
    directory_name = int(directory, 16)

    year = ((directory_name >> 25) & int("7f", 16)) + 1980
    month = (directory_name >> 21) & int("f", 16)
    day = (directory_name >> 16) & int("1f", 16)
    hour = (directory_name >> 11) & int("1f", 16)
    minute = (directory_name >> 5) & int("3f", 16)
    second = (directory_name >> 1) & int("3f", 16)

    # yyyy-MM-DD_hh_mm_ss format
    converted_name = (
        f"{year:04d}-{month:02d}-{day:02d}_" f"{hour:02d}-{minute:02d}-{second:02d}"
    )

    return converted_name


def select_from_list(selections):
    """Command line selection utility.

    Args:
        selections (list): list containing items you'd like to select.

    Returns:
        selection (int): number provided by user
        selections: returns item of type from list of choices.
    """

    print(("\n" * 2))  # spacer
    print(f"{'-' * 6} choose the best: {'-' * 6}")

    for index, option in enumerate(selections):
        print(f"{index:02d} : {option}")

    # todo: need a try statement here
    selection = int(input("select item: "))

    return (selection, selections[selection])


if __name__ == "__main__":

    help_statement = """
        **********************
        Copy path to wav_source
        Then hit "Enter"
        ----------------------
    """

    # input(help_statement)

    # get contents of clipboard
    # clipboard = cb.paste()
    clipboard = "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/wav_files_for_testing/"

    # path to wav_source that contains the audio of interest
    wav_dir_path = "/Users/peej/dev/uniden scanner scripts/uniden-api/pytest/scanner_test_data/4F067981/2019-08-06_15-12-35.wav"

    # matching tag
    tag = "Red"
    # output_file_name = "merged.wav"

    matched_files = files_with_matched_tags(clipboard, tag)
    #
    # output = merge_tagged_wav_files(matched_files)

    # todo: reset the tag to something else after it's merged

    # metadata = get_wav_meta(wav_dir_path)

    # audio_path = "/Users/peej/Downloads/uniden audio/00 HPD-NW/2019-07-05_11-39-47.wav"

    for file in matched_files:
        metadata = get_wav_meta(file)
        print(metadata)
    # metalist = re.sub(r"(?:\x00+)", "\n", metadata[0])

    # scanstring = get_string_at_offset(start, length, audio_path)
    # print(scanstring)
