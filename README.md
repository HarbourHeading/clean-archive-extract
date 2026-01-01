# Force directory in archive root

Python script extracts all archives inside `INPUT_DIR` while making sure the outputted directory only contains a root directory.

See [demo input](demo/input), for example. Where [to-archive-1](demo/input/to-archive-1) has both a directory and a file inside,
the script will extract the directory into a new directory named `to-archive-1` which contains both files inside a new root directory.

Some websites (usually user uploaded content) don't follow the standard conventions for archives, and so this is just a QoL script.
Supports `['*.zip', '*.tar', '*.tar.gz', '*.7z', '*.rar']`. Others formats can be added relatively easily. It ignores files without the set extensions.
**BEWARE:** This script will overwrite existing directories in the output directory if it finds a duplicate root directory name.

## Usage

1. Install dependencies with `pip install -r requirements.txt`.
2. Place your archives in the `INPUT_DIR` (update script variable) directory.
3. Run the script with `python main.py`.
4. The processed archives (now unarchived into a directory) will be saved in the `OUTPUT_DIR` (update script variable) directory.