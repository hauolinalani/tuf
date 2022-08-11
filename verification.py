"""
    Currently only for sdist
"""

import requests
import re
import tempfile
import os
import shutil
from in_toto.models.metadata import Metablock
from in_toto.verifylib import in_toto_verify
from securesystemslib.gpg import functions as gpg_interface

### ACCEPTING INPUTS
github_repo = "athenachernandez/tuf"
version = input("Version of TUF: ")
gpg_id = input("GPG key id for layout: ")

# Get cd key id from tagged release
site_url = f"https://github.com/{github_repo}/releases/tag/v{version}"
response = requests.get(site_url)
site_text = response.text                   # Translate site to text

pattern = "sdist.*.link"
result = re.findall(pattern, site_text)     # Find link file complete name
cd_keyid = result[0][6:-5]                  # Slice for only cd key id

### Create temporary directory
with tempfile.TemporaryDirectory() as temp_dir:     # Creates temporary folder
    # Link metadata from GitHub release
    site_url = f"https://github.com/{github_repo}/releases/download/v{version}/sdist.{cd_keyid}.link"
    response = requests.get(site_url)
    site_text = response.text                       # Translate site to text

    # Make new file in temporary directory
    release_metadata_file = open(f"{temp_dir}/sdist.{cd_keyid}.link", "w")
    release_metadata_file.write(site_text)
    release_metadata_file.close()

    # Copy .in_toto dir to temp folder
    cwd = os.getcwd()                               # Gets current directory
    source_dir = f"{cwd}/.in_toto/"
    in_toto_dir = os.listdir(f"{cwd}/.in_toto/")
    print(in_toto_dir)
    for item in in_toto_dir:
        src_file = source_dir + item
        dst_file = f"{temp_dir}/{item}"
        shutil.copyfile(src_file, dst_file)         # Copying each file

    # in-toto verify
    layout = Metablock.load(os.path.join(temp_dir, "sdist.layout"))
    layout_key_dict = {}        # Dictionary to store keys
    layout_key_dict.update(gpg_interface.export_pubkeys([gpg_id]))
    in_toto_verify(layout, layout_key_dict, link_dir_path=temp_dir)

    import pdb; pdb.set_trace()
