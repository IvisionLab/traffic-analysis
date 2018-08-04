import bpy
import bpy_extras
from mathutils import Matrix, Vector
import numpy

scene = bpy.context.scene
resolution_x_in_px = scene.render.resolution_x
resolution_y_in_px = scene.render.resolution_y

scale = scene.render.resolution_percentage / 100
pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

#---------------------------------------------------------------
# 3x4 P matrix from Blender camera
#---------------------------------------------------------------

# Build intrinsic camera parameters from Blender camera data
#
# See notes on this in 
# blender.stackexchange.com/questions/15102/what-is-blenders-camera-projection-matrix-model
def get_calibration_matrix_K_from_blender(camd):
	print(bpy.data.scenes['Car'].render.resolution_x, bpy.data.scenes['Car'].render.resolution_y)
	f_in_mm = camd.lens
	sensor_width_in_mm = camd.sensor_width
	sensor_height_in_mm = camd.sensor_height
	if (camd.sensor_fit == 'VERTICAL'):
		# the sensor HEIGHT is fixed (sensor fit is horizontal), 
		# the sensor WIDTH is effectively changed with the pixel aspect ratio
		s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio 
		s_v = resolution_y_in_px * scale / sensor_height_in_mm
	else: # 'HORIZONTAL' and 'AUTO'
		# the sensor WIDTH is fixed (sensor fit is horizontal), 
		# the sensor HEIGHT is effectively changed with the pixel aspect ratio
		"""if scene.render.pixel_aspect_x < scene.render.pixel_aspect_y:
			pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
		else:
			pixel_aspect_ratio = scene.render.pixel_aspect_y / scene.render.pixel_aspect_x
		print(pixel_aspect_ratio)"""
		s_u = resolution_x_in_px * scale * pixel_aspect_ratio / sensor_width_in_mm
		s_v = resolution_y_in_px * scale * 0.5625 / sensor_height_in_mm


	# Parameters of intrinsic calibration matrix K
	alpha_u = f_in_mm * s_u
	alpha_v = f_in_mm * s_v
	u_0 = resolution_x_in_px * scale / 2
	v_0 = resolution_y_in_px * scale / 2 

	skew = 0 # only use rectangular pixels

	# K is the camera calibration matrix (Also represented by the C letter)
	K = Matrix(
		((alpha_u, skew,    u_0),
		(    0  ,  alpha_v, v_0),
		(    0  ,    0,      1 )))
	return K


# Returns camera rotation and translation matrices from Blender.
# 
# There are 3 coordinate systems involved:
#    1. The World coordinates: "world"
#       - right-handed
#    2. The Blender camera coordinates: "bcam"
#       - x is horizontal
#       - y is up
#       - right-handed: negative z look-at direction
#    3. The desired computer vision camera coordinates: "cv"
#       - x is horizontal
#       - y is down (to align to the actual pixel coordinates 
#         used in digital images)
#       - right-handed: positive z look-at direction
def get_3x4_RT_matrix_from_blender(cam):
	# bcam stands for blender camera
	R_bcam2cv = Matrix(
				((1, 0,  0),
				 (0, -1, 0),
				 (0, 0, -1)))

	# Transpose since the rotation is object rotation, 
	# and we want coordinate rotation
	# R_world2bcam = cam.rotation_euler.to_matrix().transposed()
	# T_world2bcam = -1*R_world2bcam * location
	#
	# Use matrix_world instead to account for all constraints
	location, rotation = cam.matrix_world.decompose()[0:2]
	R_world2bcam = rotation.to_matrix().transposed()

	# Convert camera location to translation vector used in coordinate changes
	# T_world2bcam = -1*R_world2bcam*cam.location
	# Use location from matrix_world to account for constraints:     
	T_world2bcam = -1*R_world2bcam * location

	# Build the coordinate transform matrix from world to computer vision camera
	R_world2cv = R_bcam2cv*R_world2bcam
	T_world2cv = R_bcam2cv*T_world2bcam
	# put into 3x4 matrix
	RT = Matrix((
		R_world2cv[0][:] + (T_world2cv[0],),
		R_world2cv[1][:] + (T_world2cv[1],),
		R_world2cv[2][:] + (T_world2cv[2],)
	))
	return RT

def get_3x4_P_matrix_from_blender(cam):
	K = get_calibration_matrix_K_from_blender(cam.data)
	RT = get_3x4_RT_matrix_from_blender(cam)
	P = K*RT
	return P, K, RT



def project_by_object_utils(cam, point): 
	""" Alternate 3D coordinates to 2D pixel coordinate projection code """
	#scene = bpy.context.scene
	co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, point)
	#render_scale = scene.render.resolution_percentage / 100
	render_size = (
				int(scene.render.resolution_x * scale),
				int(scene.render.resolution_y * scale),
				)
	points2D = [round(co_2d.x * render_size[0]),	
				round(co_2d.y * render_size[1])]
	#return points2D ## Uncomment to set Origin at bottom-left
	points2D[1] = render_size[1] - points2D[1] # Origin at top-left
	return points2D



if __name__ == "__main__":
	render_size_y = int(scene.render.resolution_y * scale)
	print(resolution_x_in_px, resolution_y_in_px)
	
	# Insert your camera name here
	#cam = scene.objects['Camera']
	cam = bpy.data.objects['Camera']
	P, K, RT = get_3x4_P_matrix_from_blender(cam)
	
	
	
	print("==== Tests ====")
	e1 = Vector((0.895035, -2.11745, -0.660244))
	e2 = Vector((-0.8827, -2.3175, 0.6980))
	e3 = Vector((-0.8827, 2.3175, 0.6980))
	O  = Vector((0, 0,    0, 1))

	p1 = P * e1
	p1 /= p1[2] #Origin at top-left
	#p1[1] = render_size_y - p1[1] ##Uncomment to set Origin at bottom-left
	print("Projected e1")
	print(p1)
	print("proj by object_utils")
	print(project_by_object_utils(cam, Vector(e1[0:3])))
"""
	p2 = P * e2
	p2 /= p2[2]
	p2[1] = render_size_y - p2[1] ##Origin at bottom-left
	print("Projected e2")
	print(p2)
	print("proj by object_utils")
	print(project_by_object_utils(cam, Vector(e2[0:3])))

	p3 = P * e3
	p3 /= p3[2]
	p3[1] = render_size_y - p3[1] ##Origin at bottom-left
	print("Projected e3")
	print(p3)
	print("proj by object_utils")
	print(project_by_object_utils(cam, Vector(e3[0:3])))

	pO = P * O
	pO /= pO[2]
	pO[1] = render_size_y - pO[1] ##Origin at bottom-left
	print("Projected world origin")
	print(pO)
	print("proj by object_utils")
	print(project_by_object_utils(cam, Vector(O[0:3])))

	# Bonus code: save the 3x4 P matrix into a plain text file
	# Don't forget to import numpy for this
	#nP = numpy.matrix(P)
	#numpy.savetxt("/tmp/P3x4.txt", nP)  # to select precision, use e.g. fmt='%.2f'
	"""