""" This Blender script render the scene for each vehicle and save the dataset 
images and annotations.
        
"""

import bpy
import create_animation
import os
import random
import create_json as c_json
import bbox3d_coords as bb3d
import scipy.io as sio
import re
from PIL import Image
import numpy as np
import datetime
import pycococreatortool_
from sklearn import model_selection

context = bpy.context
scene = context.scene
objs = bpy.data.objects
#path_blendFile = '.'
path_blendFile =  bpy.path.abspath("//")
categories = ['bicycle', 'boat', 'chair', 'hair drier', 'car'] # Same names that COCO dataset
category_to_render = 'hair drier'
id_cat, supercategory = pycococreatortool_.category_from_name(pycococreatortool_.CATEGORIES, category_to_render)

def main():
    cars = []
    [cars.append(ob) for ob in objs if ob.name.startswith(category_to_render)]
    [poses, transform_mat, frame_end] = create_animation.main()
    objects_categories = []
    [objects_categories.append(ob) for ob in objs if any(ob.name.startswith(c) for c in categories)]

    #cars = cars[0:5]
    #frame_end = 3 
    #save_dataset_carposes(cars, poses, transform_mat, frame_end)    
    save_dataset_coco(cars, objects_categories, poses, transform_mat, frame_end)

def save_dataset_carposes(cars, poses, transform_mat, frame_end):
    """ Creates a dataset for pose classification. Each pose is saved in a 
         different folder and the JSON annotations are set.
    :param cars:
    :param poses:
    """
    dataset_path = os.path.join(path_blendFile, 'datasets','{}_{}p_native'.format(category_to_render, frame_end+1))
    scene.render.filepath = bpy.path.abspath("//")
    
    dict_vehicles = {}
    dict_poses = {}
    for car in cars:
        model_file = save_model_obj(car, dataset_path)
        [bbox3D,_] = bb3d.get_bbox3D_vertices(car)
        bboxes = []
        for i,b in enumerate(bbox3D):
            bboxes.append([b[0], b[1], b[2]])
        bbox3D = c_json.create_bbox(bboxes)
        #Only to extract dims of the models in dataset CAD CARS TORONTO (car1-car200 in our blender file)
        [width, height, length] = get_dims_car(car.name)
            
        vehicle = c_json.create_vehicle(
            dict_vehicles = dict_vehicles,
            id_model = car.name, 
            model_file = model_file, 
            bbox3D = bbox3D, 
            real_size = [width, height, length])
        dict_vehicles = vehicle
        
    for frame in range(0, frame_end+1):
        path_pose = os.path.join(dataset_path, 'Pose-%d'%frame)
        dict_vehicles_rendered = {}
        matrixP = transform_mat[frame]['matrixP']
        
        for car in cars:
            hide_show_objects(cars, hide=True)
            dict_file_names = render_image(car, path_pose, frame, dformat='carposes')
            bbox_3D_pxs = bb3d.get_bbox2D_vertices(car, matrixP)
            bboxes = []
            for i,b in enumerate(bbox_3D_pxs):
                bboxes.append([round(b[0]), round(b[1])])
            bbox_3D_pxs = c_json.create_bbox(bboxes)
            vehicle_rendered = c_json.create_vehicle_rendered(
                dict_vehicles_rendered = dict_vehicles_rendered,
                id_model = car.name,
                rgb_path = os.path.split(dict_file_names['RGB'])[-1], 
                mask_path = os.path.split(dict_file_names['MASK'])[-1], 
                depth_path = os.path.split(dict_file_names['DEPTH'])[-1], 
                render_resolution = [scene.render.resolution_x, scene.render.resolution_y],
                render_scale = scene.render.resolution_percentage,
                bbox_3D_pxs = bbox_3D_pxs)
            dict_vehicles_rendered = vehicle_rendered
        
        vK = transform_mat[frame]['K']
        vK =  [vK[0][:], vK[1][:], vK[2][:]]
        vRT = transform_mat[frame]['RT']
        vRT = [vRT[0][:], vRT[1][:], vRT[2][:]]
        pose = c_json.create_pose(
            dict_poses = dict_poses,
            id_pose = frame, 
            distance = poses[frame]['distance'],
            elevation = poses[frame]['elevation'],
            azimuth = poses[frame]['azimuth'],
            transform_mat = [vK, vRT],
            vehicles_rendered = dict_vehicles_rendered)
        dict_poses = pose        
        
    # Finally, build the json and save file
    c_json.build_json_poses(dict_vehicles, dict_poses, dataset_path)


def save_dataset_coco(cars_all, objects_categories, poses, transform_mat, frame_end):
    dataset_path = os.path.join(path_blendFile, 'datasets','{}_{}p_coco'.format(category_to_render, frame_end+1))
    scene.render.filepath = bpy.path.abspath("//")
    cars_train, cars_val = model_selection.train_test_split(cars_all, train_size=0.7, random_state=900, shuffle=True)
    #cars_val, cars_test = model_selection.train_test_split(cars_val, train_size=0.7, random_state=800, shuffle=True)
    hide_show_objects(objects_categories, hide=True)
    print('-------------- ', cars_all)
    #hide_show_objects(categories, hide=True) #TODO hide all categories
    planes = []
    [planes.append(ob) for ob in objs if ob.name.startswith('plane')]
                  
    #for cars in [cars_train, cars_val, cars_test]:
    for cars in [cars_train, cars_val]:
        dict_vehicles = {}
        dict_images = {}
        arr_dict_images =  []
        arr_dict_annotation_info =  []
        dict_annotation_info = {}
        for car in cars:
                model_file = save_model_obj(car, dataset_path)
                [bbox3D,_] = bb3d.get_bbox3D_vertices(car)
                bboxes = []
                for i,b in enumerate(bbox3D):
                    bboxes.append([b[0], b[1], b[2]])
                bbox3D = c_json.create_bbox(bboxes)
                #Only to extract dims of the models in dataset CAD CARS TORONTO (car1-car200 in our blender file)
                [width, height, length] = get_dims_car(car.name)

                dict_vehicles = c_json.create_vehicle(
                    dict_vehicles = dict_vehicles,
                    id_model = car.name, 
                    model_file = model_file, 
                    bbox3D = bbox3D, 
                    real_size = [width, height, length],
                    category = category_to_render,
                    supercategory = supercategory)

        image_info_id = 0
        annotation_info_id = 0
        for frame in range(0, frame_end+1):
           matrixP = transform_mat[frame]['matrixP']
           for car in cars: #TODO extend for other objects (for m in models)
              hide_show_objects(cars_all, hide=True)
              # Ramdonly show Backgrounds
              if random.randrange(2):
                    hide_show_objects(planes, hide=False)
                    hide_show_objects([random.choice(planes)], hide=True)
              if car in cars_train: subset = 'train2018'
              elif car in cars_val: subset = 'val2018'
              else: subset = 'test2018'
              path_image = os.path.join(dataset_path, subset)
              dict_file_names = render_image(car, path_image, frame, dformat='coco')
              bbox_3D_pxs = bb3d.get_bbox2D_vertices(car, matrixP)
              bboxes = []
              for i,b in enumerate(bbox_3D_pxs):
                 bboxes.append([round(b[0]), round(b[1])])
              bbox_3D_pxs = c_json.create_bbox(bboxes)
              vK = transform_mat[frame]['K']
              vK =  [vK[0][:], vK[1][:], vK[2][:]]
              vRT = transform_mat[frame]['RT']
              vRT = [vRT[0][:], vRT[1][:], vRT[2][:]]
              dict_images = pycococreatortool_.create_image_info(
                          image_id = image_info_id,
                          file_name = os.path.split(dict_file_names['RGB'])[-1], 
                          image_size = [scene.render.resolution_x, scene.render.resolution_y], 
                          date_captured = datetime.datetime.utcnow().isoformat(' '),
                          id_model = car.name, 
                          id_pose = frame,
                          render_resolution = [scene.render.resolution_x, scene.render.resolution_y], 
                          render_scale = scene.render.resolution_percentage, 
                          distance = poses[frame]['distance'],
                          elevation = poses[frame]['elevation'],
                          azimuth = poses[frame]['azimuth'],
                          transform_mat = [vK, vRT])
              arr_dict_images.append(dict_images)

              mask_path = os.path.join(path_image, 'MASK', dict_file_names['MASK'])
              #mask_path_absolute = os.path.join(path_blendFile, mask_path)
              binary_mask = np.asarray(Image.open(mask_path).convert('1')).astype(np.uint8)
              dict_annotation_info = pycococreatortool_.create_annotation_info(
                    annotation_id = annotation_info_id, 
                    image_id = image_info_id, 
                    binary_mask = binary_mask,
                    class_id = id_cat, 
                    is_crowd = 0,
                    bbox_3D_pxs = bbox_3D_pxs, 
                    path_mask = mask_path.replace(os.path.join(path_blendFile,'datasets')+os.sep,''),
                    image_size = None,
                    tolerance = 2, 
                    bounding_box = None)
              if dict_annotation_info is None: continue
              arr_dict_annotation_info.append(dict_annotation_info)
              image_info_id += 1
              annotation_info_id += 1

        #shutil.rmtree(os.path.join(path_image, 'MASK')) # Remove folder Mask
        # Finally, build the json and save file
        c_json.build_coco_format(models=dict_vehicles, 
                                      images=arr_dict_images, 
                                      annotations=arr_dict_annotation_info, 
                                      dataset_path=dataset_path, 
                                      subset_dir=subset)
          
def render_image(obj, dataset_path, frame=scene.frame_current, 
                 render_animation=False, dformat='carposes'):
    """ Render and save each frame (in files).

    :param obj: Object to render, in this case a car.
    :param frame: Animation frame to render 
    :param dataset_path: path to save the dataset
    """
    global scene
    hide_show_objects([obj], hide = False)
    
    # Set the index to render objects and childrens
    obj.pass_index = 5
    for child in obj.children:
            child.pass_index = 5

    dict_file_names = set_render_path(scene, dataset_path, obj.name, frame, dformat)
    if render_animation:
        bpy.ops.render.render(animation = True)
    else:
        scene.frame_set(frame)
        bpy.ops.render.render(write_still = False)
    return dict_file_names
    

def hide_show_objects(objs, hide):
    """hide objects and don´t render these.

    :param objs:
    :param hide (boolean): True hide objects, and False show them.    
    """
    for ob in objs: 
        ob.hide = hide
        ob.hide_render = hide
        for child in ob.children:
            child.hide = hide
            child.hide_render = hide


def set_render_path(scene, path, ob_name, frame=None, dformat='carposes'):
    dict_file_names = {}
    for node in scene.node_tree.nodes:
        if node.type == 'OUTPUT_FILE':
            extension = '.' + node.format.file_format.lower()
            if extension=='.jpeg': extension='.jpg'
            node.base_path = os.path.join(path, node.name)
            file_name = ob_name + '-'
            node.mute = False
            if dformat == 'coco':
                if node.name == 'RGB': node.base_path = os.path.join(path, '')
                elif node.name == 'MASK': node.base_path = os.path.join(path, node.name)
                else: node.mute = True #Not renderize
                file_name = 'CP_' + os.path.basename(path) + ob_name + '-'
            node.file_slots[0].path = file_name
            if not frame==None:
                file_name_com = os.path.split(scene.render.frame_path(frame=frame))[-1]
                file_name_com = file_name_com.replace(os.path.splitext(file_name_com)[-1], extension)
                file_name = file_name + file_name_com
                dict_file_names[node.name] = file_name               
    return dict_file_names

# Not used now
def save_model_stl(obj, path):
    """ Export an STL file for an object """
    # Create Directory (If Necessary)
    dir_models = os.path.join(path,'MODELS')
    if not os.path.exists(dir_models): os.makedirs(dir_models)
    
    filepath = os.path.join(dir_models, obj.name + '.stl')
    bpy.ops.export_mesh.stl(filepath = filepath)
    return filepath


def save_model_obj(obj, path):
    """ Export an 3ds file for an object """
    global scene, objs
    dir_models = os.path.join(path,'MODELS')
    if not os.path.exists(dir_models): os.makedirs(dir_models)    # Create Directory (If Necessary)
    filepath = os.path.join(dir_models, obj.name + '.obj')
    
    scene.objects.active = None
    for o in objs:
        o.select = False
        for child in o.children:
            child.select = False
    
    obj.select = True
    for child in obj.children:
            child.select = True
    scene.objects.active = obj
    bpy.ops.export_scene.obj(filepath = filepath, use_selection = True)
    filepath.replace(path_blendFile,'')
    return filepath
    

def get_dims_car(car_name):
    """ Read the specific mat file from dataset (CAD Models)
    and get the real dimensions of an specific car. This function used only to 
    create our dataset, after that, it will be commented. """
    number = re.findall("\d+", car_name)
    name_file = 'car_'+'{:03d}'.format(int(number[0]))+'_mesh.mat'
    #path_datacar = os.path.join(path_blendFile, os.pardir, 'skp', name_file)
    path_datacar = os.path.join(path_blendFile, 'skp', name_file)
    size = [None, None, None] # [width, height,length]
    if os.path.exists(path_datacar): 
        mat_file = sio.loadmat(path_datacar)
        if 'dims' in mat_file['mesh'].dtype.names: 
            dims = mat_file['mesh']['dims']
            #[width, height,length] = [int(dims[0][0][0][0]), int(dims[0][0][0][1]), int(dims[0][0][0][2])]
            for i,s in enumerate(dims[0][0][0]):
                size[i] = int(s)
    return size


if __name__ == "__main__":
    main()


