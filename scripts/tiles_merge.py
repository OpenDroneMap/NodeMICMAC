#!/usr/bin/env python
from __future__ import division, print_function
import os
from glob import glob
import argparse
import numpy as np
from skimage.io import imread, imsave
import PIL.Image
PIL.Image.MAX_IMAGE_PIXELS = None

def arrange_tiles(flist, args):
    tmp_inds = [os.path.splitext(f)[0].split('Tile_')[-1].split('_') for f in flist]
    arr_inds = np.array([[int(a) for a in ind] for ind in tmp_inds])
    nrows = arr_inds[:,1].max() + 1
    ncols = arr_inds[:,0].max() + 1
    img_arr = np.array(np.zeros((nrows, ncols)), dtype='object')
    for i in range(nrows):
         for j in range(ncols):
             img_arr[i, j] = imread(os.path.sep.join([args.imgdir, '{}_Tile_{}_{}.tif'.format(args.filename, j, i)]))
    return img_arr


def main():
    parser = argparse.ArgumentParser(description="Re-stitch images tiled by MicMac.",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-filename', action='store', type=str, default='Orthophotomosaic',
                        help="MicMac filename to tile [Orthophotomosaic]")
    parser.add_argument('-imgdir', action='store', type=str, default='Ortho-MEC-Malt',
                        help="Directory containing images [.]")
    args = parser.parse_args()
    
    filelist = glob(os.path.sep.join([args.imgdir, '{}_Tile*'.format(args.filename)]))
    
    tiled = arrange_tiles(filelist, args)
    I, J = tiled.shape

    arr_cols = []
    for j in range(J):
        arr_cols.append(np.concatenate(tiled[:,j], axis=0))
        
    img = np.concatenate(arr_cols, axis=1)
    
    imsave(os.path.sep.join([args.imgdir, '{}.tif'.format(args.filename)]), img)
    

if __name__ == "__main__":
    main()
