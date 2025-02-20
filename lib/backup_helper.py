import tarfile
from datetime import datetime
from os import path, getenv, remove
import sh

directories = ['.screenly', 'screenly_assets']
default_archive_name = "screenly-backup"
static_dir = "screenly/static"


def create_backup(name=default_archive_name):
    home = getenv('HOME')
    archive_name = "{}-{}.tar.gz".format(
        name if name else default_archive_name,
        datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    )
    file_path = path.join(home, static_dir, archive_name)
    if path.isfile(file_path):
        remove(file_path)

    try:
        with tarfile.open(file_path, "w:gz") as tar:

            for directory in directories:
                path_to_dir = path.join(home, directory)
                tar.add(path_to_dir, arcname=directory)
    except IOError as e:
        remove(file_path)
        raise e

    return archive_name


def recover(file_path):
    with tarfile.open(file_path, "r:gz") as tar:
        for directory in directories:
            if directory not in tar.getnames():
                raise Exception("Archive is wrong.")

        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=getenv("HOME","/home/pi"))

    remove(file_path)
