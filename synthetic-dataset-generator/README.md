# A TOOL FOR BUILDING MULTI-PURPOSE AND MULTI-POSE, SYNTHETIC DATA

This is the code for our tool to generate multi-purpose, synthetic data sets from multiple camera viewpoints and environmental conditions. The set of rendered images provide data that can be used for geometric computer vision problems, such as: Depth estimation, camera pose estimation, 3D box estimation, 3D reconstruction, camera calibration, and also pixel-perfect ground truth for scene understanding problems, such as: Semantic segmentation, instance segmentation, object detection, just to cite a few. It contains a wide set of features easy to extend, besides allowing for building sets of images in the well-known MSCOCO format, so ready for deep learning works.

<div style="text-align:center"><img src="https://github.com/IvisionLab/traffic-analysis/blob/master/synthetic-dataset-generator/figures/outputs.png" width="60%" height="60%"></div>

## System requirements

To run the generator, you need [Blender](https://github.com/dfelinto/blender), [Python >=3.0], and some libraries:

pip3 install numpy scikit-image scikit-learn scipy

pip3 install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI

* This code was tested on an Ubuntu 18.04 system using Blender 2.8. All the scripts should be executed from the Blender script window.

## Build your own dataset

![Steps](https://github.com/IvisionLab/traffic-analysis/blob/master/synthetic-dataset-generator/figures/steps.png)

To generate any data set, three steps are required: locate 3D models in the scene (blender file), set the discretization parameters, and run the generator (render_dataset.py).

Link to the .Blender files Car poses and Object poses: https://drive.google.com/drive/folders/1vCy-kKYWWpEdFUymwD71pNCX4MPmXcyV?usp=sharing

An example of a generated dataset is the Car poses dataset with +270k images from +2k categorized poses and perfect automatic annotations.

![Car poses](https://github.com/IvisionLab/traffic-analysis/blob/master/synthetic-dataset-generator/figures/examples2.png){:height="40%" width="40%"}

![Others](https://github.com/IvisionLab/traffic-analysis/blob/master/synthetic-dataset-generator/figures/examples3.png){:height="40%" width="40%"}

## Request Dataset
Please send an e-mail to lrebouca@ufba.br to receive a link to any of our datasets generated explained in the paper (Car, Bike, Chair, Boat or Hairdryer poses). Your e-mail must be sent from a valid institutional account, and include the following text (copy and paste the text below, filling the required fields):

"Subject: Request to download synthetic poses dataset.

Name: [your first and last name]
Affiliation: [university where you work]
Department: [your department]
Current position: [your job title]
E-mail: [must be the e-mail at the above mentioned institution]
Dataset: [e.g., Car poses]

[your signature]"  

P.S. A link to the dataset file will be sent as soon as possible.

## Paper and Citation
If you find this useful in your research please cite the [paper](http://ivisionlab.ufba.br/doc/publication/2019/VIPIMAGE_tool_for_building_datasets.pdf).  If you find this code useful in your research, please consider citing:

    @inproceedings{plummerCITE201z,
	Author = {Ruiz Marco and Fontinele Jefferson and Perrone Ricardo and Santos Marcelo and Oliveira Luciano},
	Title = {A Tool for Building Multi-purpose and Multi-pose Synthetic Data Sets},
	Booktitle  = {ECCOMAS THEMATIC CONFERENCE ON COMPUTATIONAL VISION AND MEDICAL IMAGE PROCESSING, Lecture Notes in Computational Vision and Biomechanics},
	Year = {2019}
    }


