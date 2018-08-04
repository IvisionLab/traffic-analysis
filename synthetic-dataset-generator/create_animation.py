""" This Blender script creates an animation to simulate a camera rotating
on a 3D sphere space.

:param GRADES_STEP: 	   Grades' incrementation for elevation and azimuth.
:param DISTANCE_STEP:   Meters' incrementation for distance camera-object.
:param RANGE_DISTANCE:  Distances from Camera to Sphere (e.g. 7m:50m each 1m).
:param RANGE_ELEVATION: Elevations of the Camera (e.g. 0°:90° each 5°).
:param RANGE_AZIMUTH:	Azimuths of the Camera (e.g. 0°:355° each 5°).
"""

import bpy
from math import radians
import proj_matrix as prj_mat
import numpy as np

# Configure these discretization parameters
DISTANCE_STEP = 1
GRADES_STEP = 20
RANGE_DISTANCE = np.arange(2, 4+1, DISTANCE_STEP, dtype=np.float64)
RANGE_ELEVATION = np.arange(10, 30+1, GRADES_STEP, dtype=np.float64)
RANGE_AZIMUTH = np.arange(0, 180+1, GRADES_STEP, dtype=np.float64)


# Get selected Sphere, Camera and blender context
context = bpy.context
scene = context.scene
sphere = scene.objects['Sphere']
camera = scene.objects['Camera']
poses = {}
transform_mat = {}


def main():
	initialize_first_frame()
	# Create animation
	for distance in RANGE_DISTANCE:
		for elevation in RANGE_ELEVATION:
			azimuth_rotator(distance, elevation)
	
	# Set the Start & End frames
	bpy.context.scene.frame_preview_start = 0
	bpy.context.scene.frame_preview_end = frame-1
	bpy.data.scenes[0].frame_start = 0
	bpy.data.scenes[0].frame_end = frame-1
	return poses, transform_mat, frame-1


def initialize_first_frame():
	""" Initialize the first frame to default values """
	global scene, sphere, camera, frame, poses, transform_mat
	scene.frame_current = 0
	sphere.animation_data_clear()
	sphere.rotation_euler = (0,0,0)
	camera.animation_data_clear()
	camera.rotation_euler = (radians(90),0,0)	
	frame = 0
	poses = {}
	transform_mat = {}


def azimuth_rotator(distance, elevation):
	""" Azimuth rotator from 0 to 355 grades (pose in 360° = 0°). """
	global frame, poses, transform_mat, camera, sphere
	for azimuth in RANGE_AZIMUTH:
		sphere.rotation_euler = (radians(-elevation), 0, radians(azimuth))
		sphere.keyframe_insert(data_path="rotation_euler", frame=frame)
		
		# Relocate the Camera
		camera.location = (0, -distance, 0)
		camera.keyframe_insert(data_path='location', frame=frame)
		#print("Pose %d: %d, %d, %d" %(frame,-distance, elevation, azimuth))
		poses[frame] = {'distance':-distance, 'elevation': elevation, 'azimuth': float(azimuth)}
		scene.update()
		[matrixP, K, RT] = prj_mat.get_3x4_P_matrix_from_blender(camera)
		transform_mat[frame] = {'matrixP': matrixP, 'K': K, 'RT': RT}
		frame+=1
			


if __name__ == "__main__":
	[poses, transform_mat, frame_end] = main()
	print(poses)


