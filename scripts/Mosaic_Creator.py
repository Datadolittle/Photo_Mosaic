import os, random

import numpy as np
from PIL import Image


def get_images(images_directory):
    images = []
    for file_name in os.listdir(images_directory):
        file_path = os.path.join(images_directory, file_name)
        with open(file_path, 'rb') as f:
            im = Image.open(f)
            im.load()
        images.append(im)

    return images


def get_average_rgb_value(image):
    im = np.array(image)
    w, h, d = im.shape
    return tuple(np.average(im.reshape(w * h, d), axis=0))


def split_image(image, size):
    original_width, original_height = image.size[0], image.size[1]
    m, n = size
    w, h = int(original_width / n), int(original_height / m)
    imgs = []
    for j in range(m):
        for i in range(n):
            imgs.append(image.crop((i * w, j * h, (i + 1) * w, (j + 1) * h)))
    return imgs


def get_best_match_index(input_avg, avgs):
    avg = input_avg
    index = 0
    min_index = 0
    min_dist = float("inf")
    for val in avgs:
        dist = ((val[0] - avg[0]) * (val[0] - avg[0]) +
                (val[1] - avg[1]) * (val[1] - avg[1]) +
                (val[2] - avg[2]) * (val[2] - avg[2]))
        if dist < min_dist:
            min_dist = dist
            min_index = index
        index += 1
    return min_index


def create_image_grid(images, dims):
    m, n = dims
    width = max([img.size[0] for img in images])
    height = max([img.size[1] for img in images])
    grid_img = Image.new('RGB', (n * width, m * height))
    for index in range(len(images)):
        row = int(index / n)
        col = index - n * row
        grid_img.paste(images[index], (col * width, row * height))
    return grid_img


def createPhotomosaic(target_image, input_images, grid_size, reuse_images=True):
    target_patches = split_image(target_image, grid_size)

    output_images = []
    count = 0
    batch_size = int(len(target_patches) / 10)

    candidate_imgs_avg_rgb_values = [get_average_rgb_value(img) for img in input_images]

    for patch in target_patches:
        target_patch_abg_rgb = get_average_rgb_value(patch)
        match_index = get_best_match_index(target_patch_abg_rgb, candidate_imgs_avg_rgb_values)
        output_images.append(input_images[match_index])
        if count > 0 and batch_size > 10 and count % batch_size is 0:
            print(f'processed {count} of {len(target_patches)}...')
        count += 1
        # remove selected image from input if flag set
        if not reuse_images:
            input_images.remove(match_index)

    mosaic_image = create_image_grid(output_images, grid_size)
    return mosaic_image


def main(target_image, patch_images_dir, save_path, patch_size=50, reuse_images=True):
    target_image = Image.open(target_image)
    # Get image size

    # Adjust size to fit closest number of patches


    patch_images = get_images(patch_images_dir)
    print('resizing images...')
    for img in patch_images:
        img.thumbnail((patch_size, patch_size))

    # check if any valid input images found
    if patch_images == []:
        raise ValueError(f'No input images found in {patch_images_dir}. Exiting.')

    # shuffle list - to get a more varied output?
    random.shuffle(patch_images)

    # size of grid
    grid_size = (patch_size, patch_size)

    # output
    output_filename = 'mosaic_elise.jpeg'
    if save_path:
        output_filename = save_path

    print('starting photomosaic creation...')
    # if images can't be reused, ensure m*n <= num_of_images
    if not reuse_images:  # TODO - Change condition
        if grid_size[0] * grid_size[1] > len(patch_images):
            raise ValueError('grid size less than number of images')

    # create photomosaic
    mosaic_image = createPhotomosaic(target_image, patch_images, grid_size, reuse_images)

    # write out mosaic
    mosaic_image.save(output_filename, 'jpeg')

    print(f'saved output to {output_filename}')



if __name__ == '__main__':
    main(os.path.join(os.path.dirname(__file__), '..', 'data', 'Tree.jpg'),
         os.path.join(os.path.dirname(__file__), '..', 'data', 'Trees'),
         os.path.join(os.path.dirname(__file__), '..', 'data'))
