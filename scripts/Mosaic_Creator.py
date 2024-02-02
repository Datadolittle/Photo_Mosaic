#!/usr/bin/env python
import os, random, argparse
from PIL import Image
import numpy as np

parser = argparse.ArgumentParser(description='Creates a photomosaic from input images')
parser.add_argument('--target', dest='target', required=True, help="Image to create mosaic from")
parser.add_argument('--images', dest='images', required=True, help="Diectory of images")
parser.add_argument('--grid', nargs=2, dest='grid', required=True, help="Size of photo mosaic")
parser.add_argument('--output', dest='output', required=False)
parser.add_argument('--reuse', dest='reuse', action='store_true')
parser.add_argument('--no-reuse', dest='reuse', action='store_false')
parser.set_defaults(reuse=True)
parser.add_argument('--resize', dest='resize', action='store_true')
parser.add_argument('--no-resize', dest='resize', action='store_false')
parser.set_defaults(resize=True)
parser.add_argument('--shuffle', dest='shuffle', action='store_true',help='Whether shuffle the sequence when setting the grids')
parser.set_defaults(shuffle=False)
parser.add_argument('--alpha', nargs=2, dest='alpha', type=int, help='The alpha values for images and target-image, in the range [0, 255]')
parser.set_defaults(alpha=[255, 0])
parser.add_argument('--magnify', nargs=1, dest='magnification', type=float, help='Enlarge the final out_img, float type')
parser.set_defaults(magnification=(1.0,))


args = parser.parse_args()

MATCH_INDECES = []

def getImages(images_directory):
    files = os.listdir(images_directory)
    images = []
    for file in files:
        filePath = os.path.abspath(os.path.join(images_directory, file))
        try:
            fp = open(filePath, "rb")
            im = Image.open(fp)
            images.append(im)
            im.load()
            fp.close()
        except:
            print("Invalid image: %s" % (filePath,))
    return (images)


def getAverageRGB(image):
    im = np.array(image)
    w, h, d = im.shape
    return (tuple(np.average(im.reshape(w * h, d), axis=0)))


def splitImage(image, size):
    W, H = image.size[0], image.size[1]
    m, n = size
    w, h = int(W / n), int(H / m)
    imgs = []
    for j in range(m):
        for i in range(n):
            imgs.append(image.crop((i * w, j * h, (i + 1) * w, (j + 1) * h)))
    return (imgs)


def getBestMatchIndex(input_avg, avgs):
    avg = input_avg
    index = 0
    min_index = 0
    min_dist = float("inf")
    for val in avgs:
        dist = ((val[0] - avg[0]) * (val[0] - avg[0]) +
                (val[1] - avg[1]) * (val[1] - avg[1]) +
                (val[2] - avg[2]) * (val[2] - avg[2]))
        if dist < min_dist and index not in MATCH_INDECES:
            min_dist = dist
            min_index = index
        index += 1
    # Global store of matched indexes if no reuse
    if not reuse_images:
        MATCH_INDECES.append(min_index)

    return (min_index)


def createImageGrid(images, dims):
    m, n = dims
    width = max([img.size[0] for img in images])
    height = max([img.size[1] for img in images])
    grid_img = Image.new('RGBA', (n * width, m * height))   # always set as RGBA, until writing out img then check whether discard alpha 
    for index in range(len(images)):
        row = int(index / n)
        col = index - n * row
        grid_img.paste(images[index], (col * width, row * height))
    return (grid_img)


def createPhotomosaic(target_image, input_images, grid_size,
                      reuse_images,#useless?
                      if_shuffle,
                      alpha_input):
    target_images = splitImage(target_image, grid_size)

    # init a list. Using list[index] to set elements, no list.append().
    output_images = list(range(len(target_images)))

    count = 0
    batch_size = int(len(target_images) / 10)
    avgs = []
    for img in input_images:
        try:
            avgs.append(getAverageRGB(img))
        except ValueError:
            # If no append inf, avgs_index and  input_imgs_index will not correspond
            avgs.append((float("inf"),float("inf"),float("inf")))   
            print("An unsafe img is found, you may need to run Image_Tester.py to delete it")
            continue

    grid_indices = np.arange(len(target_images))
    if (if_shuffle):
        np.random.shuffle(grid_indices) # shuffle the indexes

    for index in grid_indices:
        img=target_images[index]
        avg = getAverageRGB(img)
        match_index = getBestMatchIndex(avg, avgs)
        output_images[index]=input_images[match_index] # set the grid
        if count > 0 and batch_size > 10 and count % batch_size is 0:
            print('processed %d of %d...' % (count, len(target_images)))
        count += 1


    mosaic_image = createImageGrid(output_images, grid_size)

    mosaic_image = mosaic_image.convert("RGBA")   #default 255
    target_image = target_image.convert("RGBA")

    # resize the target_image, matching the final out-img
    target_image = target_image.resize(mosaic_image.size)

    if not alpha_input[0] == 255:
        mosaic_image.putalpha(alpha_input[0])

    if not alpha_input[1] == 255:
        target_image.putalpha(alpha_input[1])


    # merge target_image and Composite img
    mosaic_image = Image.alpha_composite(mosaic_image, target_image)    # RGBA
    return (mosaic_image)


### ---------------------------------------------

# alpha value of imgs and target_img
alpha_input = args.alpha

target_image = Image.open(args.target)

# input images
print('reading input folder...')
input_images = getImages(args.images)

# check if any valid input images found
if input_images == []:
    print('No input images found in %s. Exiting.' % (args.images,))
    exit()


# size of grid
grid_size = (int(args.grid[1]), int(args.grid[0]))

# output
output_filename = 'mosaic.jpeg'
if args.output:
    output_filename = args.output

# re-use any image in input
reuse_images = args.reuse

# resize the input to fit original image size?
resize_input = args.resize

# If true, set the grids in random order, rather than ascending order.
shuffle_input = args.shuffle

# magnification for final output
magnify = args.magnification[0]

print('starting photomosaic creation...')

# if images can't be reused, ensure m*n <= num_of_images
if not reuse_images:
    if grid_size[0] * grid_size[1] > len(input_images):
        print('grid size less than number of images')
        exit()

# resizing input
if resize_input:
    print('resizing images...')
    # for given grid size, compute max dims w,h of tiles
    dims = (int(target_image.size[0]*magnify / grid_size[1]),
            int(target_image.size[1]*magnify / grid_size[0]))

    # resize
    for i, img in enumerate(input_images):
        input_images[i] = img.resize((dims)) 
        # If imgs are small size, thumbnail may make [black strap] between every grids
        # So, using resize() insteadly, even though potential performance overhead.

# create photomosaic
mosaic_image = createPhotomosaic(target_image, input_images, grid_size, reuse_images,shuffle_input,alpha_input)

# write out mosaic
mosaic_image.convert("RGB").save(output_filename, 'jpeg') # always output as jpeg to handle incorrect alpha band

print("saved output to %s" % (output_filename,))
print('done.')
