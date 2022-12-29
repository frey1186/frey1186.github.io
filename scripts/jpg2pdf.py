#!/usr/bin/env python
#
# Convert a lot of images to one PDF file.
# version: v0.1
# date: 2022-12-22
#
from PIL import Image
import sys
import os 

if len(sys.argv) < 2 :
    print("Usage: %s Image_dir output.pdf"%sys.argv[0])
    sys.exit()

img_path = sys.argv[1]
out_pdf = sys.argv[2]

imgs = list()
for root,dirs,files in os.walk(img_path):
    for f in files:
        fn = os.path.join(root,f)
        if os.path.splitext(f)[1] not in ['.jpeg','.png','.JPEG','PNG']:
            print("%s is NOT a image file, Ignored."%f)
            continue
        img = Image.open(fn)
        imgs.append(img)

img0 = imgs[0]
img0.save(out_pdf, "PDF", resolution=100.0, save_all=True, append_images=imgs[1:])
