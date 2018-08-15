# A TOOL FOR BUILDING MULTI-PURPOSE AND MULTI-POSE, SYNTHETIC DATA

This is the code for our tool to generate multi-purpose, synthetic data sets from multiple camera viewpoints and environmental conditions is proposed here. The set of rendered images provide data that can be used for geometric computer vision problems, such as: Depth estimation, camera pose estimation, 3D box estimation, 3D reconstruction, camera calibration, and also pixel-perfect ground truth for scene understanding problems, such as: Semantic segmentation, instance segmentation, object detection, just to cite a few. It contains a wide set of features easy to extend, besides allowing for building sets of images in the well-known MSCOCO format, so ready for deep learning works.




## System requirements

To run the generator, you need [Blender](https://github.com/dfelinto/blender), [Python >=3.0].

pip3 install numpy scikit-image scikit-learn scipy

pip3 install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI



## Build your own

![Steps](https://github.com/IvisionLab/traffic-analysis/blob/master/synthetic-dataset-generator/figures/steps.png)

To generate any data set, three steps are required: locate 3D models in the scene, set the discretization parameters, and run the generator. Follow the next instructions.

 

## Paper and Citation
If you find this useful in your research please cite:

> Cite in APA format: XXXXXX
    
> @paper{	xx,
	Author = {Ruiz Marco and Fontinele Jefferson and Perrone Ricardo and Santos Marcelo and Oliveira Luciano},
	title     = {Microsoft {COCO:} Common Objects in Context},
	journal   = {xx},
	volume    = {xx},
	year      = {2018},
	eprint    = {xx},
	pages={xx--xx}
}



