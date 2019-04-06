import cv2
import os
import numpy as np
import pickle
from dataset_preparation import mean_method,load_pickle
from tqdm import tqdm


# ----- grid size adjusting ----- #

def grid_adjust(init_grid, im_shape):
    h_im, w_im = im_shape

    if len(init_grid) == 1:
        grid = (init_grid[0], init_grid[0])

        return grid

    if h_im < w_im:  # Landscape:
        grid = sorted(init_grid)
    else:
        grid = sorted(init_grid, reverse=True)

    return grid


# ----- Reshaping ----- #
def new_lenght(mini_length, big_length):
    rest = big_length % mini_length
    if rest == 0:
        return big_length
    else:
        if rest < mini_length / 2:
            return big_length - rest

        else:
            return big_length + mini_length - rest


def reshaping(im, grid_size):
    h_im, w_im, _ = im.shape
    grid_size = grid_adjust(grid_size, (h_im, w_im))
    h_grid, w_grid = grid_size
    new_h_im, new_w_im = new_lenght(h_grid, h_im), new_lenght(w_grid, w_im)

    if h_im != new_h_im or w_im != new_w_im:
        im = cv2.resize(im, (new_w_im, new_h_im))

    return im, grid_size


# ----- Extracting ----- #

def closest_node(query_value, pickler_values):
    pickler_values = np.asarray(pickler_values)
    dist_2 = np.sum((pickler_values - query_value) ** 2, axis=1)
    return np.argmin(dist_2)


def pickler_matching(thumbnail, list_best_matches_paths, img_paths, pickler_values):
    query_value = mean_method(thumbnail)

    nearest_ind = closest_node(query_value, pickler_values)

    list_best_matches_paths.append(img_paths[nearest_ind])


def target_extraction(im, pickler_path, grid_size, thumb_size):
    pickler = load_pickle(pickler_path)
    img_paths = pickler["img_paths"]
    pickler_values = pickler["values"]
    h_im, w_im, _ = im.shape
    step_h, step_w = h_im // grid_size[0], w_im // grid_size[1]

    list_best_matches_paths = []

    print("Finding Best Matches")
    for ind_h in tqdm(range(0, h_im, step_h), desc='Big loop1'):
        for ind_w in range(0, w_im, step_w):
            crop_im = im[ind_h:ind_h + step_h, ind_w:ind_w + step_w]
            pickler_matching(crop_im, list_best_matches_paths, img_paths, pickler_values)
            # mask = np.zeros((h_im, w_im), dtype=np.uint8)
            # mask[ind_h:ind_h + step_h, ind_w:ind_w + step_w] = 255
            # cv2.imshow("little cropping", cv2.bitwise_and(im, im, mask=mask))
            # cv2.waitKey(100)
    print("\nBest Matches Found - Building big image !")

    h_res, w_res = thumb_size * grid_size[0], thumb_size * grid_size[1]
    step_h, step_w = h_res // grid_size[0], w_res // grid_size[1]

    result_im = np.zeros((h_res, w_res, 3), dtype=np.uint8)
    for ind_h in tqdm(range(0, h_res, step_h), desc='Big loop2'):
        for ind_w in tqdm(range(0, w_res, step_w), desc='Small loop2'):
            best_match = list_best_matches_paths.pop(0)
            result_im[ind_h:ind_h + step_h, ind_w:ind_w + step_w] = cv2.resize(cv2.imread(best_match), (step_w, step_h))

    print("DONE !")

    return result_im


def save_im_result(im, grid_size, thumb_size, save_path="img_result"):
    grid_size = args['grid_size']
    thumb_size = args["thumbnail_size"]

    ind = 0

    while "the name already exist":
        name = "{}/result_grid_{}_thumb_{}_{}.jpg".format(os.path.abspath(save_path),
                                                          grid_size[0], thumb_size, ind)

        if not os.path.isfile(name):
            break
        else:
            ind += 1

    cv2.imwrite(name, im)


# ----- Main ----- #
def main_process(args):
    query_path = args['query_path']
    grid_size = args['grid_size']
    pickler_path = args["pickler_path"]
    thumb_size = args["thumbnail_size"]

    im_init = cv2.imread(query_path)

    im, grid_size = reshaping(im_init, grid_size)

    im_result = target_extraction(im, pickler_path, grid_size, thumb_size)

    save_im_result(im_result, grid_size, thumb_size)

    cv2.imshow("initial img", im_init)
    cv2.imshow("im after reshape", im)
    cv2.namedWindow("im_result", cv2.WINDOW_KEEPRATIO)
    cv2.imshow("im_result", im_result)

    cv2.waitKey()


if __name__ == '__main__':
    args_query_path = "img_examples/" + "rsln.jpg"
    args_pickler_path = "pickler/" + "mia_182_imgs_0.p"
    args_thumbnail_size = 50
    # args_grid_size = (64, 36)
    # args_grid_size = (64,)
    args_grid_size = (128,)
    # args_grid_size = (18, 32)

    args = {
        "query_path": args_query_path,
        "pickler_path": args_pickler_path,
        "grid_size": args_grid_size,
        "thumbnail_size": args_thumbnail_size,

    }

    main_process(args)
