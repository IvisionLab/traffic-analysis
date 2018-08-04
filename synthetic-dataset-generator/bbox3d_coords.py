"""
    #         
    # Create a 3D bounding box arround the car mesh.
    #  ________ 
    # |\       |\        Faces:
    # |_\______|_\        0 : Ground     (vertex: 0,1,2,3)
    # \ |      \ |        1 : Top     (vertex: 4,7,6,5)
    #  \|_______\|        2 : Right    (vertex: 2,6,7,3)
    #                        3 : Front    (vertex: 1,5,6,2)
    #                         4 : Left    (vertex: 0,4,5,1)
    #                         5 : Back     (vertex: 4,0,3,7)    
    #
    #
"""

import bpy
from bpy_extras import *
from mathutils import Vector

scene = bpy.context.scene
camera = scene.objects['Camera']


def get_bbox2D_vertices(car, matrixP):
    [bbox3D,_] = get_bbox3D_vertices(car)
    bbox2D = [get_coord_cameraview(matrixP, point3D) for point3D in bbox3D]
    return bbox2D
        

def get_coord_cameraview(matrixP, point3D, resolution_y = scene.render.resolution_y, 
                                 scale = scene.render.resolution_percentage/100):
    point2D = matrixP * point3D
    point2D /= point2D[2] #Origin at top-left
    ##point2D[1] = render_size_y - point2D[1] # Uncomment these 2 lines to set Origin at bottom-left
    ##render_size_y = int(resolution_y * scale)
    
    print("------------------------")
    point2D[0:3] = [round(point2D[0]), round(point2D[1]), round(point2D[2])]
    print('3D POINT: ')
    print(point3D)
    print('2D POINT (CALCULATED): ')
    print(point2D[0:2])
    print('2D POINT (BLENDER): ')
    print(get_coord_cameraview2(point3D))
    
    if point2D[0]-get_coord_cameraview2(point3D)[0]==0 and point2D[1]-get_coord_cameraview2(point3D)[1]==0:
        print("PERFECT!")
    else:
        print("------------------------------------------------                    OOPSSSSSSSSSSSSS!")
    return point2D[0:2]


def get_bbox3D_vertices(car):
    """ Adapted from https://blender.stackexchange.com/a/38210/53016 """
    minx, miny, minz = (999999.0,)*3
    maxx, maxy, maxz = (-999999.0,)*3

    for v in car.bound_box:
        v_world = car.matrix_world * Vector((v[0],v[1],v[2]))
        
        if v_world[0] < minx:
            minx = v_world[0]
        if v_world[0] > maxx:
            maxx = v_world[0]

        if v_world[1] < miny:
            miny = v_world[1]
        if v_world[1] > maxy:
            maxy = v_world[1]

        if v_world[2] < minz:
            minz = v_world[2]
        if v_world[2] > maxz:
            maxz = v_world[2]

    width = (maxx-minx)/2
    depth = (maxz-minz)/2
    height = (maxy-miny)/2
    
    verts = [(+1.0, +1.0, -1.0),
             (+1.0, -1.0, -1.0),
             (-1.0, -1.0, -1.0),
             (-1.0, +1.0, -1.0),
             (+1.0, +1.0, +1.0),
             (+1.0, -1.0, +1.0),
             (-1.0, -1.0, +1.0),
             (-1.0, +1.0, +1.0)]

    # ground, top, right, front, left, back
    faces = [(0, 1, 2, 3),
             (4, 7, 6, 5),
             (0, 4, 5, 1),
             (1, 5, 6, 2),
             (2, 6, 7, 3),
             (4, 0, 3, 7)]

    # apply size
    verts = [Vector((v[0] * width, v[1] * height,  v[2] * depth)) for v in verts]
    return verts, faces



def get_coord_cameraview2(point3D):
    #Returns the camera space coords for a 3d point. called NDC.
    co_2d = object_utils.world_to_camera_view(scene, camera, point3D)
    
    # Now the pixel coords:
    render_scale = scene.render.resolution_percentage / 100
    render_size = (int(scene.render.resolution_x * render_scale), 
                   int(scene.render.resolution_y * render_scale))
    points2D = [round(co_2d.x * render_size[0]),    
                round(co_2d.y * render_size[1])]
    #return points2D ## Uncomment to set Origin at bottom-left
    points2D[1] = render_size[1] - points2D[1] # Origin at top-left
    return points2D

