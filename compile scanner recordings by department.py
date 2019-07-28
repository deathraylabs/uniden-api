from tinytag import TinyTag
from pathlib import Path
import shutil

# folder that the user_rec folders were transferred to
uniden_folder = "/Users/Peej/Downloads/uniden audio/"

# Path object for the root of our folder tree
basepath = Path(uniden_folder)

# todo: change logic to use pathlib instead of shutil
for folder in basepath.iterdir():
    if folder.is_dir():
        # the .glob ensures that we only get audio files, no hidden files
        for file in folder.glob("*.wav"):
            # create tinytag object that contains metadata
            tag = TinyTag.get(file)
            # get the department name, which is stored under title
            department = tag.title
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
                p.mkdir(exist_ok=True)  # wont overwrite existing directory
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
