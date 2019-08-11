import pytest

from pathlib import Path
from scanner.scanner_utility_functions import *


def test_get_wav_meta():
    # static test file
    directory = "./scanner_test_data/4F067981/2019-08-06_15-12-35.wav"
    p = Path(directory)

    meta_output = get_wav_meta(directory)

    assert p.is_file()
    assert type(meta_output) == dict

    return meta_output


if __name__ == "__main__":
    test_get_wav_meta()
