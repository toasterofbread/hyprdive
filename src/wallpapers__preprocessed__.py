# NOTE: This file was automatically generated from:
# /home/toaster/Programs/applications/hyprdive/src/wallpapers.py
# DO NOT CHANGE DIRECTLY! 1749837458.6936288
import os
try:
    join, = ultraimport('__dir__/os.path/__init__.py', objects_to_import=('join',), recurse=True)
except ultraimport.ResolveImportError as e:
    try:
        join, = ultraimport('__dir__/os.path.py', objects_to_import=('join',), recurse=True)
    except ultraimport.ResolveImportError as e2:
        raise ultraimport.RewrittenImportError(code_info=('from os.path import join, expanduser', '/home/toaster/Programs/applications/hyprdive/src/wallpapers.py', 2, 0), object_to_import='join', combine=[e, e2]) from None
try:
    expanduser, = ultraimport('__dir__/os.path/__init__.py', objects_to_import=('expanduser',), recurse=True)
except ultraimport.ResolveImportError as e:
    try:
        expanduser, = ultraimport('__dir__/os.path.py', objects_to_import=('expanduser',), recurse=True)
    except ultraimport.ResolveImportError as e2:
        raise ultraimport.RewrittenImportError(code_info=('from os.path import join, expanduser', '/home/toaster/Programs/applications/hyprdive/src/wallpapers.py', 2, 0), object_to_import='expanduser', combine=[e, e2]) from None
try:
    seed, = ultraimport('__dir__/random/__init__.py', objects_to_import=('seed',), recurse=True)
except ultraimport.ResolveImportError as e:
    try:
        seed, = ultraimport('__dir__/random.py', objects_to_import=('seed',), recurse=True)
    except ultraimport.ResolveImportError as e2:
        raise ultraimport.RewrittenImportError(code_info=('from random import seed, randrange, sample, shuffle', '/home/toaster/Programs/applications/hyprdive/src/wallpapers.py', 3, 0), object_to_import='seed', combine=[e, e2]) from None
try:
    randrange, = ultraimport('__dir__/random/__init__.py', objects_to_import=('randrange',), recurse=True)
except ultraimport.ResolveImportError as e:
    try:
        randrange, = ultraimport('__dir__/random.py', objects_to_import=('randrange',), recurse=True)
    except ultraimport.ResolveImportError as e2:
        raise ultraimport.RewrittenImportError(code_info=('from random import seed, randrange, sample, shuffle', '/home/toaster/Programs/applications/hyprdive/src/wallpapers.py', 3, 0), object_to_import='randrange', combine=[e, e2]) from None
try:
    sample, = ultraimport('__dir__/random/__init__.py', objects_to_import=('sample',), recurse=True)
except ultraimport.ResolveImportError as e:
    try:
        sample, = ultraimport('__dir__/random.py', objects_to_import=('sample',), recurse=True)
    except ultraimport.ResolveImportError as e2:
        raise ultraimport.RewrittenImportError(code_info=('from random import seed, randrange, sample, shuffle', '/home/toaster/Programs/applications/hyprdive/src/wallpapers.py', 3, 0), object_to_import='sample', combine=[e, e2]) from None
try:
    shuffle, = ultraimport('__dir__/random/__init__.py', objects_to_import=('shuffle',), recurse=True)
except ultraimport.ResolveImportError as e:
    try:
        shuffle, = ultraimport('__dir__/random.py', objects_to_import=('shuffle',), recurse=True)
    except ultraimport.ResolveImportError as e2:
        raise ultraimport.RewrittenImportError(code_info=('from random import seed, randrange, sample, shuffle', '/home/toaster/Programs/applications/hyprdive/src/wallpapers.py', 3, 0), object_to_import='shuffle', combine=[e, e2]) from None
try:
    make_collage, = ultraimport('__dir__/collage_maker/__init__.py', objects_to_import=('make_collage',), recurse=True)
except ultraimport.ResolveImportError as e:
    try:
        make_collage, = ultraimport('__dir__/collage_maker.py', objects_to_import=('make_collage',), recurse=True)
    except ultraimport.ResolveImportError as e2:
        raise ultraimport.RewrittenImportError(code_info=('from .collage_maker import make_collage', '/home/toaster/Programs/applications/hyprdive/src/wallpapers.py', 4, 0), object_to_import='make_collage', combine=[e, e2]) from None
import json
WALLPAPER_DIR = expanduser('~/Media/Wallpapers/')
SETS_DIR = expanduser('~/Media/Wallpapers/Sets')
IMAGE_FILETYPES = ['png', 'jpg', 'jpeg', 'webp']
USED_FILES_LIST_PATH = expanduser('~/Media/Wallpapers/.wallpaper_files_in_use')
MAIN_DIR = join(WALLPAPER_DIR, 'Active')

def isFileType(filePath: str, filetypes: list[str]):
    for filetype in filetypes:
        if filePath.endswith(f'.{filetype}'):
            return True
    return False

def getNextTempImageFile(extension: str=''):
    i = 0
    while True:
        file = f'/tmp/hyprdive_gen_image_{i}{extension}'
        if not os.path.exists(file):
            return file
        i += 1

def generateCollageFromImages(images: list[str]):
    shuffle(images)
    file = getNextTempImageFile('.png')
    res = make_collage(images, file, 1920, 400, 1080, brightness=0.8)
    return file

def getActiveWallpaperImages(used_files: list, directory: str=MAIN_DIR) -> (list[str], dict):
    wallpaper_files = []
    last_set_info = {}
    for file in os.listdir(directory):
        if file.startswith('.'):
            continue
        file_path = join(directory, file)
        if file.endswith('.set'):
            with open(file_path, 'r') as f:
                last_set_info = json.loads(f.read().strip())
            if 'set_path' in last_set_info:
                set_path = expanduser(last_set_info['set_path'])
            else:
                set_path = join(SETS_DIR, last_set_info['set_name'])
            if not os.path.isdir(set_path):
                print('Set not found: ' + set_path)
                continue
            for root, dirs, files in os.walk(set_path):
                for set_file in files:
                    set_file_path = join(root, set_file)
                    if set_file_path in used_files or not isFileType(set_file_path, IMAGE_FILETYPES):
                        continue
                    wallpaper_files.append(set_file_path)
            continue
        if file_path in used_files or not isFileType(file_path, IMAGE_FILETYPES):
            continue
        wallpaper_files.append(file_path)
    return (wallpaper_files, last_set_info)

def getRandomWallpaper(used_files: list, directory: str=MAIN_DIR):
    wallpaper_files, set_content = getActiveWallpaperImages(used_files, directory)
    if len(wallpaper_files) == 0:
        return None
    if set_content['collage'] == True:
        collage_images = sample(wallpaper_files, min(len(wallpaper_files), 20))
        for file in collage_images:
            used_files.append(file)
        return generateCollageFromImages(collage_images)
    else:
        ret = wallpaper_files[randrange(len(wallpaper_files))]
        used_files.append(ret)
        return ret

def getUsedFilesList(used_files: list) -> list[str]:
    if not os.path.isfile(USED_FILES_LIST_PATH):
        return []
    with open(USED_FILES_LIST_PATH, 'r') as f:
        return json.reads(f.read())

def updateUsedFilesList(used_files: list):
    with open(USED_FILES_LIST_PATH, 'w') as f:
        f.write(json.dumps(used_files))