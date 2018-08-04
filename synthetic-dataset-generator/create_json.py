
import json
import os
import bpy
import pycococreatortool_

path_blendFile =  bpy.path.abspath("//")


def build_json_poses(vehicles, poses, dataset_path):
    """ """
    json_data = {'vehicles': vehicles, 'poses': poses}
    
    with open(os.path.join(dataset_path, 'dataset1.json'), 'w') as f:
        #json.dump(json_data, f, indent=3, separators=(', ', ': '))
        json.dump(json_data, f)
    print("OK")
    return json_data

def create_vehicle(dict_vehicles, id_model, model_file, bbox3D, real_size, supercategory='vehicle', category='car'):
    """  """
    model_file = path_relative(model_file)
    dict_vehicles[id_model] = {
        'supercategory': supercategory,
        'category': category, 
        'model_file': model_file, 
        'bbox3D_model': bbox3D,
        'real_size': {'width': real_size[0], 'height': real_size[1], 'length': real_size[2]}
    }
              
    return dict_vehicles

def create_bbox(bbox):
    """ Create a dictionary for: 2D coordinates (in NDC), or 3D (x,y,z) coordinates.
         0-3 = lower corners & 4-7 = upper corners """
    element = {
        'ground':     {0: bbox[0], 1: bbox[1], 2: bbox[2], 3: bbox[3]},
        'top'   :     {4: bbox[4], 7: bbox[7], 6: bbox[6], 5: bbox[5]},
        'right' :     {2: bbox[2], 6: bbox[6], 7: bbox[7], 3: bbox[3]},
        'front' :     {1: bbox[1], 5: bbox[5], 6: bbox[6], 2: bbox[2]},
        'left'  :     {0: bbox[0], 4: bbox[4], 5: bbox[5], 1: bbox[1]},
        'back'  :     {4: bbox[4], 0: bbox[0], 3: bbox[3], 7: bbox[7]}
    }
    return element



def create_vehicle_rendered(dict_vehicles_rendered, id_model, rgb_path, mask_path, depth_path, render_resolution, 
                            render_scale, bbox_3D_pxs):
    """  """
    # TODO: Get and Save 2D Boxes from Masks, using blender
    rgb_path = path_relative(rgb_path)
    mask_path = path_relative(mask_path)
    depth_path = path_relative(depth_path)
    dict_vehicles_rendered[id_model] = {
        'path_rgb': rgb_path,    
        'path_mask': mask_path,    
        'path_depth': depth_path, 
        'render_resolution': render_resolution, 
        'render_scale': render_scale/100, 
        'bbox_3D_pxs': bbox_3D_pxs
    }
    return dict_vehicles_rendered


def create_pose(dict_poses, id_pose, distance, elevation, azimuth, transform_mat, vehicles_rendered):
    """  """
    dict_poses[id_pose] = {
        'distance'    : distance,
        'elevation'    : elevation,
        'azimuth'    : azimuth,
        'transformation_matrix': {'K': transform_mat[0], 'RT': transform_mat[1]},
        'vehicles_rendered' : vehicles_rendered
    }
    return dict_poses


def path_relative(path):
    """  """
    return path.replace(path_blendFile,'.'+os.sep)
    

#%%--------------------------------------------------- COCO DATASET FORMAT 
def build_coco_format(models, images, annotations, dataset_path, subset_dir, 
                      info=pycococreatortool_.INFO, licenses=pycococreatortool_.LICENSES, 
                      categories=pycococreatortool_.CATEGORIES):
    """ Build dataset annotations in COCO Dataset Format """        
    json_data = {
        'info': pycococreatortool_.INFO,
        'licenses': pycococreatortool_.LICENSES,
        'categories': pycococreatortool_.CATEGORIES,
        'models': models,
        'images': images,
        'annotations': annotations    
    }
    dir_annotations = os.path.join(dataset_path,'annotations')
    if not os.path.exists(dir_annotations): os.makedirs(dir_annotations)
    path_json = os.path.join(dir_annotations, 'instances_{}.json'.format(subset_dir))
    with open(path_json, 'w') as f:
       json.dump(json_data, f)
    print("OK")
    return json_data


