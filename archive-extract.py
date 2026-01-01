"""Clean archive extract

Examples:
    python archive-extract.py

Author: Harbourheading
Creation: 2026-01-01
"""

import os
import shutil
import tarfile
import tempfile
import zipfile
from glob import glob
from multiprocessing.pool import Pool
from os.path import basename, join

import py7zr
import rarfile

INPUT_DIR = join('demo', 'input')
OUTPUT_DIR = join('demo', 'output')
EXTENSIONS = ['*.zip', '*.tar', '*.tar.gz', '*.7z', '*.rar']

filenames = []
for ext in EXTENSIONS:
    filenames.extend(glob(join(INPUT_DIR, ext)))


def _get_root_items(filename: str) -> set[str]:
    root_items: set[str] = set()
    try:
        if tarfile.is_tarfile(filename):
            with tarfile.open(filename, 'r') as f:
                names = [m.name for m in f]
        elif zipfile.is_zipfile(filename):
            with zipfile.ZipFile(filename, 'r') as f:
                names = [m.filename for m in f.infolist()]
        elif rarfile.is_rarfile(filename):
            with rarfile.RarFile(filename, 'r') as f:
                names = [m.filename for m in f.infolist()]
        elif py7zr.is_7zfile(filename):
            with py7zr.SevenZipFile(filename, mode='r') as f:
                names = [m.filename for m in f.list()]
        else:
            return root_items

        for name in names:
            root = name.split('/')[0]
            if root:
                root_items.add(root)
    except Exception:
        pass
    return root_items


def _extract(filename: str, path: str):
    if tarfile.is_tarfile(filename):
        with tarfile.open(filename, 'r') as f:
            f.extractall(path)
    elif zipfile.is_zipfile(filename):
        with zipfile.ZipFile(filename, 'r') as f:
            f.extractall(path)
    elif rarfile.is_rarfile(filename):
        with rarfile.RarFile(filename, 'r') as f:
            f.extractall(path)
    elif py7zr.is_7zfile(filename):
        with py7zr.SevenZipFile(filename, mode='r') as f:
            f.extractall(path)


def process_archive(filename: str):
    root_items = _get_root_items(filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Base name for the output directory (remove all extensions)
    name = basename(filename)
    for extension in ['.tar.gz', '.zip', '.tar', '.7z', '.rar']:
        if name.lower().endswith(extension):
            name = name[:-len(extension)]
            break
            
    out_dir = join(OUTPUT_DIR, name)
    
    # If the output directory already exists, we will extract into it.
    # To handle potential race conditions and ensure a clean extraction,
    # we use a temporary directory first.
    os.makedirs(out_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        _extract(filename, temp_dir)
        if len(root_items) == 1:
            root_item = list(root_items)[0]
            extracted_item = join(temp_dir, root_item)
            if os.path.isdir(extracted_item) and root_item == name:
                # If it's already a single directory with the same name, 
                # move its contents to out_dir to avoid name/name/ nesting
                for item in os.listdir(extracted_item):
                    dest = join(out_dir, item)
                    if os.path.exists(dest):
                        if os.path.isdir(dest):
                            shutil.rmtree(dest)
                        else:
                            os.remove(dest)
                    shutil.move(join(extracted_item, item), dest)
            else:
                dest = join(out_dir, root_item)
                if os.path.exists(dest):
                    if os.path.isdir(dest):
                        shutil.rmtree(dest)
                    else:
                        os.remove(dest)
                shutil.move(extracted_item, dest)
        else:
            for item in os.listdir(temp_dir):
                dest = join(out_dir, item)
                if os.path.exists(dest):
                    if os.path.isdir(dest):
                        shutil.rmtree(dest)
                    else:
                        os.remove(dest)
                shutil.move(join(temp_dir, item), dest)


def run(pool: Pool):
    pool.map(process_archive, filenames)


if __name__ == '__main__':
    with Pool() as p:
        run(p)
