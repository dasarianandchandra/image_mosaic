import time
import os
from tqdm import tqdm
import cv2
import pickle
from settings import *
import sys
import numpy as np


def load_pickle(pickle_path):
    pickle_in = open(pickle_path, "rb")

    return pickle.load(pickle_in)


def merge_pickles(pickle_path1, pickle_path2, save_path):
    pickler1 = load_pickle(pickle_path1)
    img_paths1 = pickler1["img_paths"]
    pickler_values1 = pickler1["values"]

    pickler2 = load_pickle(pickle_path2)
    img_paths2 = pickler2["img_paths"]
    pickler_values2 = pickler2["values"]

    save_pickle(save_path, img_paths1 + img_paths2, pickler_values1 + pickler_values2)


def save_pickle(save_path, list_img_paths, list_values, name=None):
    dico = {
        "img_paths": list_img_paths,
        "values": list_values
    }
    ind = 0
    if name is None:
        prefix = "dataset"
    else:
        prefix = name

    while "the name already exist":
        pickler_name = "{}/{}_{}_imgs_{}.p".format(os.path.abspath(save_path), prefix, len(list_img_paths),
                                                   ind)

        if not os.path.isfile(pickler_name):
            break
        else:
            ind += 1

    outfile = open(pickler_name, 'wb')
    pickle.dump(dico, outfile)
    outfile.close()


def get_path(dataset_folder, keep_downloads=False):
    not_used_folders = ["downloads", "Archives"]
    subfolders = [f.path for f in os.scandir(dataset_folder)
                  if f.is_dir() and not f.path.endswith(tuple(not_used_folders))]
    list_img_paths = []
    if len(subfolders) > 0:
        for subfolder in subfolders:
            for file in [f.path for f in os.scandir(subfolder) if f.is_file() and f.path.endswith(tuple(extensions))]:
                list_img_paths.append(file)
    else:
        for file in [f.path for f in os.scandir(dataset_folder) if f.is_file() and f.path.endswith(tuple(extensions))]:
            list_img_paths.append(file)
    return list_img_paths


def mean_method(im):
    return np.mean(im, axis=tuple(range(im.ndim - 1)))


def apply_method(list_img_paths, method=0):
    list_values = []
    new_list_img_paths = []
    # for img_path in list_img_paths:
    for img_path in tqdm(list_img_paths, total=len(list_img_paths)):
        try:
            im = cv2.imread(img_path)

        except Exception as e:
            print("Problem occurs when reading img: {}".format(e))
            print("Guilty img: {}".format(img_path))

        else:
            if im is not None and im.shape[0] != 0 and im.shape[1] != 0:
                value = mean_method(im)
                list_values.append(value)
                new_list_img_paths.append(img_path)
            else:
                print("\nimpossible to read img")
                print("Guilty img: {}".format(img_path))

    return new_list_img_paths, list_values


def main_process(dataset_folder, name=None, save_path_pickler="pickler", keep_downloads=False):
    dataset_folder = os.path.abspath(dataset_folder)
    list_img_paths = get_path(dataset_folder, keep_downloads=keep_downloads)
    new_list_img_paths, list_values = apply_method(list_img_paths)

    save_pickle(save_path_pickler, new_list_img_paths, list_values, name=name)


if __name__ == '__main__':
    # main_process("/media/hdd_linux/Images")
    main_process("/media/hdd_linux/Images/Archives/mia khalifa", name="mia")
