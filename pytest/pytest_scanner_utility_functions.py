import pytest

from pathlib import Path
from scanner.scanner_utility_functions import *


def test_get_wav_meta():
    # static test file
    directory = "./scanner_test_data/4F067981/2019-08-06_15-12-35.wav"
    p = Path(directory)

    meta_output = get_wav_meta(directory)
    assert meta_output["Site:Name"] == "98 HOU PubSafety NW Simulcast"
    assert meta_output["Channel:Name"] == "01 HPD-N"

    assert p.is_file()
    assert type(meta_output) == dict

    return meta_output


def test_files_with_matched_tags():
    """Check against test directory."""

    tag = "Red"
    directory = "./scanner_test_data/wav_files_for_testing"
    p = Path(directory)

    assert p.is_dir()

    files = files_with_matched_tags(directory, tag)

    assert type(files) == list


# if __name__ == "__main__":
#     test_get_wav_meta()
