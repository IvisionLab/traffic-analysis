#!/usr/bin/env python3

import re
import datetime
import numpy as np
from itertools import groupby
from skimage import measure
from PIL import Image
import sys
#sys.path.append('/home/marco/anaconda3/lib/python3.6/site-packages/')
sys.path.append('/home/marco/marco-mask2/lib/python3.6/site-packages')
from pycocotools import mask

INFO = {
    'description': 'OBJECT POSES DATASET',
    'url' : 'https://github.com/marcoruizrueda/carposes_creator_dataset/',
    'version': '0.1.0',
    'year': 2018,
    'contributor': 'marcoruizrueda',
    'date_created': datetime.datetime.utcnow().isoformat(' ')
}

LICENSES = [{
    'id': 1,
    'name': 'Attribution-NonCommercial-ShareAlike License',
    'url': 'http://creativecommons.org/licenses/by-nc-sa/2.0/'
}]

CATEGORIES = [
{"supercategory": "person","id": 1,"name": "person"},
{"supercategory": "vehicle","id": 2,"name": "bicycle"},
{"supercategory": "vehicle","id": 3,"name": "car"},
{"supercategory": "vehicle","id": 4,"name": "motorcycle"},
{"supercategory": "vehicle","id": 5,"name": "airplane"},
{"supercategory": "vehicle","id": 6,"name": "bus"},
{"supercategory": "vehicle","id": 7,"name": "train"},
{"supercategory": "vehicle","id": 8,"name": "truck"},
{"supercategory": "vehicle","id": 9,"name": "boat"},
{"supercategory": "outdoor","id": 10,"name": "traffic light"},
{"supercategory": "outdoor","id": 11,"name": "fire hydrant"},
{"supercategory": "outdoor","id": 13,"name": "stop sign"},
{"supercategory": "outdoor","id": 14,"name": "parking meter"},
{"supercategory": "outdoor","id": 15,"name": "bench"},
{"supercategory": "animal","id": 16,"name": "bird"},
{"supercategory": "animal","id": 17,"name": "cat"},
{"supercategory": "animal","id": 18,"name": "dog"},
{"supercategory": "animal","id": 19,"name": "horse"},
{"supercategory": "animal","id": 20,"name": "sheep"},
{"supercategory": "animal","id": 21,"name": "cow"},
{"supercategory": "animal","id": 22,"name": "elephant"},
{"supercategory": "animal","id": 23,"name": "bear"},
{"supercategory": "animal","id": 24,"name": "zebra"},
{"supercategory": "animal","id": 25,"name": "giraffe"},
{"supercategory": "accessory","id": 27,"name": "backpack"},
{"supercategory": "accessory","id": 28,"name": "umbrella"},
{"supercategory": "accessory","id": 31,"name": "handbag"},
{"supercategory": "accessory","id": 32,"name": "tie"},
{"supercategory": "accessory","id": 33,"name": "suitcase"},
{"supercategory": "sports","id": 34,"name": "frisbee"},
{"supercategory": "sports","id": 35,"name": "skis"},
{"supercategory": "sports","id": 36,"name": "snowboard"},
{"supercategory": "sports","id": 37,"name": "sports ball"},
{"supercategory": "sports","id": 38,"name": "kite"},
{"supercategory": "sports","id": 39,"name": "baseball bat"},
{"supercategory": "sports","id": 40,"name": "baseball glove"},
{"supercategory": "sports","id": 41,"name": "skateboard"},
{"supercategory": "sports","id": 42,"name": "surfboard"},
{"supercategory": "sports","id": 43,"name": "tennis racket"},
{"supercategory": "kitchen","id": 44,"name": "bottle"},
{"supercategory": "kitchen","id": 46,"name": "wine glass"},
{"supercategory": "kitchen","id": 47,"name": "cup"},
{"supercategory": "kitchen","id": 48,"name": "fork"},
{"supercategory": "kitchen","id": 49,"name": "knife"},
{"supercategory": "kitchen","id": 50,"name": "spoon"},
{"supercategory": "kitchen","id": 51,"name": "bowl"},
{"supercategory": "food","id": 52,"name": "banana"},
{"supercategory": "food","id": 53,"name": "apple"},
{"supercategory": "food","id": 54,"name": "sandwich"},
{"supercategory": "food","id": 55,"name": "orange"},
{"supercategory": "food","id": 56,"name": "broccoli"},
{"supercategory": "food","id": 57,"name": "carrot"},
{"supercategory": "food","id": 58,"name": "hot dog"},
{"supercategory": "food","id": 59,"name": "pizza"},
{"supercategory": "food","id": 60,"name": "donut"},
{"supercategory": "food","id": 61,"name": "cake"},
{"supercategory": "furniture","id": 62,"name": "chair"},
{"supercategory": "furniture","id": 63,"name": "couch"},
{"supercategory": "furniture","id": 64,"name": "potted plant"},
{"supercategory": "furniture","id": 65,"name": "bed"},
{"supercategory": "furniture","id": 67,"name": "dining table"},
{"supercategory": "furniture","id": 70,"name": "toilet"},
{"supercategory": "electronic","id": 72,"name": "tv"},
{"supercategory": "electronic","id": 73,"name": "laptop"},
{"supercategory": "electronic","id": 74,"name": "mouse"},
{"supercategory": "electronic","id": 75,"name": "remote"},
{"supercategory": "electronic","id": 76,"name": "keyboard"},
{"supercategory": "electronic","id": 77,"name": "cell phone"},
{"supercategory": "appliance","id": 78,"name": "microwave"},
{"supercategory": "appliance","id": 79,"name": "oven"},
{"supercategory": "appliance","id": 80,"name": "toaster"},
{"supercategory": "appliance","id": 81,"name": "sink"},
{"supercategory": "appliance","id": 82,"name": "refrigerator"},
{"supercategory": "indoor","id": 84,"name": "book"},
{"supercategory": "indoor","id": 85,"name": "clock"},
{"supercategory": "indoor","id": 86,"name": "vase"},
{"supercategory": "indoor","id": 87,"name": "scissors"},
{"supercategory": "indoor","id": 88,"name": "teddy bear"},
{"supercategory": "indoor","id": 89,"name": "hair drier"},
{"supercategory": "indoor","id": 90,"name": "toothbrush"}]

convert = lambda text: int(text) if text.isdigit() else text.lower()
natrual_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]

def category_from_name(dict_categories, name):
    for c in dict_categories:
        if c['name'] == name: 
            id_cat = c['id']
            category = c['supercategory']
            return id_cat, category
    return None

def resize_binary_mask(array, new_size):
    image = Image.fromarray(array.astype(np.uint8)*255)
    image = image.resize(new_size)
    return np.asarray(image).astype(np.bool_)

def close_contour(contour):
    if not np.array_equal(contour[0], contour[-1]):
        contour = np.vstack((contour, contour[0]))
    return contour

def binary_mask_to_rle(binary_mask):
    rle = {'counts': [], 'size': list(binary_mask.shape)}
    counts = rle.get('counts')
    for i, (value, elements) in enumerate(groupby(binary_mask.ravel(order='F'))):
        if i == 0 and value == 1:
                counts.append(0)
        counts.append(len(list(elements)))

    return rle

def binary_mask_to_polygon(binary_mask, tolerance=0):
    """Converts a binary mask to COCO polygon representation

    Args:
        binary_mask: a 2D binary numpy array where '1's represent the object
        tolerance: Maximum distance from original points of polygon to approximated
            polygonal chain. If tolerance is 0, the original coordinate array is returned.

    """
    polygons = []
    # pad mask to close contours of shapes which start and end at an edge
    padded_binary_mask = np.pad(binary_mask, pad_width=1, mode='constant', constant_values=0)
    contours = measure.find_contours(padded_binary_mask, 0.5)
    contours = np.subtract(contours, 1)
    for contour in contours:
        contour = close_contour(contour)
        contour = measure.approximate_polygon(contour, tolerance)
        if len(contour) < 3:
            continue
        contour = np.flip(contour, axis=1)
        segmentation = contour.ravel().tolist()
        # after padding and subtracting 1 we may get -0.5 points in our segmentation 
        segmentation = [0 if i < 0 else i for i in segmentation]
        polygons.append(segmentation)

    return polygons

def create_image_info(image_id, file_name, image_size, 
                      id_model, id_pose, render_resolution, render_scale, 
                      distance, elevation, azimuth, transform_mat, 
                      date_captured=datetime.datetime.utcnow().isoformat(' '),
                      license_id=1, coco_url="", flickr_url=""):
    dict_images = {
            "id": image_id,
            "file_name": file_name,
            "width": image_size[0],
            "height": image_size[1],
            "date_captured": date_captured,
            "license": license_id,
            "coco_url": coco_url,
            "flickr_url": flickr_url,
            "id_model": id_model,
            "id_pose": id_pose,
            "render_resolution": render_resolution,
            'render_scale': render_scale/100,
            "distance": distance,
            "elevation": elevation,
            "azimuth": azimuth,
            'transformation_matrix': {'K': transform_mat[0], 'RT': transform_mat[1]},
            "elevation": elevation
    }
    return dict_images


def create_annotation_info(annotation_id, image_id, binary_mask,
                           class_id, is_crowd,  bbox_3D_pxs, path_mask, 
                           image_size=None, tolerance=2, bounding_box=None):
    
    #category_info = {'id': class_id, 'is_crowd': is_crowd}
    binary_mask_encoded = mask.encode(np.asfortranarray(binary_mask.astype(np.uint8)))

    area = mask.area(binary_mask_encoded)
    if area < 1:
        return None

    if bounding_box is None:
        bounding_box = mask.toBbox(binary_mask_encoded)

    if is_crowd:
        segmentation = binary_mask_to_rle(binary_mask)
    else :
        segmentation = binary_mask_to_polygon(binary_mask, tolerance)
        if not segmentation:
            return None

    dict_annotation_info = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": class_id,
        "iscrowd": is_crowd,
        "area": area.tolist(),
        "bbox": bounding_box.tolist(),
        "segmentation": segmentation,
        "width": binary_mask.shape[1],
        "height": binary_mask.shape[0],
        "path_mask": path_mask,
        "bbox_3D_pxs": bbox_3D_pxs
    } 
    return dict_annotation_info