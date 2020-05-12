# Docker Containers for Training and Deploying Models to Edge Devices

For now there are two docker file in this directory:
## TOCO Converter Tool
`toco-Dockerfile` can quantize and convert a frozen graph to a tflite model with TOCO tools. This container is especially useful for models trained with TensorFlow Object detection API with just specifying the path to the exported frozen graph with following commands:
### Build Container From Source:
```
# 1- Clone the repository
git clone https://github.com/neuralet/neuralet
cd training/tf_object_detection_api

# 2- Build the container
docker build -f toco-Dockerfile -t "neuralet/toco" .

3- Run the container
docker run -v [PATH_TO_FROZEN_GRAPH_DIRECTORY]:/model_dir neuralet/toco --graph_def_file=[frozen graph file]
```

### Pull container From Dockerhub:
```
docker run -v [PATH_TO_FROZEN_GRAPH_DIRECTORY]:/model_dir neuralet/toco --graph_def_file=[frozen graph file]

```
these commands will create a `detect.tflite` file in the graph def directory you mounted to the docker.
you can also specify other parameters like:
`--input_shapes [default is 1,300,300,3]`
`--inference_type [default is QUANTIZED_UINT8]`

## TensorFlow Object Detection API
`tensorflow-od-api-Dockerfile` will install the TensorFlow Object Detection API and its dependecies in the `/models/research/object_detection` directory. For instructions to train an object detection model visit [API's Github Repo](https://github.com/tensorflow/models/tree/master/research/object_detection).
Run followings to use this container with CPU support:
### Build Container From Source:
```
# 1- Clone the repository
git clone https://github.com/neuralet/neuralet
cd training/tf_object_detection_api

# 2- Build the container
docker build -f tensorflow-od-api-Dockerfile -t "neuralet/tensorflow-od-api" .

3- Run the container
docker run -it -v [PATH TO EXPERIMENT DIRECTORY]:/work neuralet/tensorflow-od-api
```
### Pull container From Dockerhub:
```
docker run -it -v [PATH TO EXPERIMENT DIRECTORY]:/work neuralet/tensorflow-od-api

``` 
Run followings to use this container with GPU support:

### Build Container From Source:
```
# 1- Clone the repository
git clone https://github.com/neuralet/neuralet
cd training/tf_object_detection_api

# 2- Build the container
docker build -f tensorflow-od-api-Dockerfile -t "neuralet/tensorflow-od-api" .

3- Run the container
docker run -it --gpus all -v [PATH TO EXPERIMENT DIRECTORY]:/work neuralet/tensorflow-od-api
```
### Pull container From Dockerhub:
```
docker run -it --gpus all -v [PATH TO EXPERIMENT DIRECTORY]:/work neuralet/tensorflow-od-api

```


note that you should install [Nvidia Docker Toolkit](https://github.com/NVIDIA/nvidia-docker) for gpu support.

