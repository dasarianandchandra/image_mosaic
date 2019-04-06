import os
import google_images_download
from tqdm import tqdm
import cv2
from settings import *


def is_image_useable(im_path):
    im = cv2.imread(im_path)
    if im is not None and im.shape[0] != 0 and im.shape[1] != 0:
        return
    else:
        return False


def deplace_and_rename(output_folder, download_folder):
    # subfolders = [f.path for f in os.scandir(download_folder) if f.is_dir()]

    for root, dirs, files in os.walk(download_folder):
        if root != download_folder:
            dir_name = os.path.basename(root)
            new_folder_name = os.path.join(output_folder, dir_name)
            if not os.path.exists(new_folder_name):
                os.makedirs(new_folder_name)
                # for (i, name) in enumerate([file for file in files if file.endswith(tuple(extensions))]):
                for (i, name) in enumerate(files):
                    actual_path = os.path.join(root, name)
                    new_name = "{:04d}_{}{}".format(i, dir_name, os.path.splitext(name)[1])
                    if is_image_useable(actual_path):
                        os.rename(actual_path, os.path.join(new_folder_name, new_name))
                    else:
                        print("Image removed : {}".format(actual_path))
            else:
                ind = 0
                for name in files:
                    actual_path = os.path.join(root, name)
                    while "the name already exist":
                        new_name = "{:04d}_{}{}".format(ind, dir_name, os.path.splitext(name)[1])
                        if not os.path.isfile(os.path.join(new_folder_name, new_name).replace(". ", "_")):
                            break
                        else:
                            ind += 1
                    if is_image_useable(actual_path):
                        os.rename(actual_path, os.path.join(new_folder_name, new_name).replace(". ", "_"))

                    else:
                        print("Image removed : {}".format(actual_path))
            os.rmdir(root)


def main_process(renaming=False):
    output_folder = "/media/hdd_linux/Images"
    output_folder = os.path.abspath(output_folder)
    download_folder = os.path.abspath(output_folder) + "/downloads"
    aspect_ratio = "wide"

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    nbr_per_request = 300

    requests = [
        "landscape",
        "mountain",
        "sea",
        "ocean",
        "sky",
        "forest",
        "nature",
        "spring",
        "autumn",
        "winter",
        "summer",

    ]
    for request in tqdm(requests, total=len(requests)):
        command_list = ["googleimagesdownload",
                        "-o", download_folder,
                        "-k", request,
                        "-l", str(nbr_per_request),
                        "-a", "{}".format(aspect_ratio),
                        "--chromedriver", "/usr/bin/chromedriver",
                        ]

        command = " ".join(command_list)

        os.system(command)

    if renaming:
        deplace_and_rename(output_folder, download_folder)


if __name__ == '__main__':
    main_process(renaming=True)

    # is_image_useable("/media/hdd_linux/Images/downloads/mountain/8.jpg")
