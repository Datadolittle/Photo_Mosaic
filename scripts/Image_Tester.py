#!/usr/bin/env python
#Importing the required libraries
import os, random, argparse
from PIL import Image
import numpy as np

parser = argparse.ArgumentParser(description='Checks background images for correct number of channels')
parser.add_argument('--images', dest='images', required=True, help="Diectory of images")

args = parser.parse_args()


moveme = []
## This tests to make sure the dimensions of all the photos are the same
for filename in os.listdir(args.images):
    path = args.images+filename
    try:
        x = Image.open(path)
        im = np.array(x)
        try:
            w, h, d = im.shape
        except:
            moveme.append(filename)
    except:
        continue
    
if (len(moveme) > 0):
    command = "mkdir Unusable_Images"
    os.system(command)
    for item in moveme:
        q = '"' + args.images+item + '"'
        command = "mv " + q + " Unusable_Images/"
        os.system(command)

    
  

