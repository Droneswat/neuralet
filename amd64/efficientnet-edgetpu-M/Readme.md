# Coral efficientnet-edgetpu-M model:
This is a dockerized implementation of the [Coral](https://coral.ai/) Efficientnet medium for amd64 host with an attached USB coral edge tpu accelerator. [Link to the original model.](https://github.com/google-coral/edgetpu/raw/master/test_data/efficientnet-edgetpu-M_quant_edgetpu.tflite)

Efficientnet-M (medium size) is a member of efficientnet family introduced by Mingxing Tan and Quoc V. Le in the paper [EfficientNet: Rethinking Mo del Scaling for Convolutional Neural Networks](https://arxiv.org/abs/1905.11946), which achieve state-of-the-art accuracy, yet being an order-of-magnitude smaller and faster than previous models.

This classification model is trained on [ImageNet](http://www.image-net.org/) dataset and can recognize 1000 different object categories. The input image size of the network must be ```240x240```.

# Codebase architecture:
The ```server-example.py``` is responsible to run inference on the input image and put the result in the output queue. The server will automatically download the edge-TPU compiled tflite model from [neuralet](https://github.com/neuralet/neuralet-models) if it doesn't exist under ```data/models```. The server will start automatically when the container starts.

The ```client.py``` contains a simple script that allows user to prepare their input data and push it to the queue. The input of the server should be a RGB image with the shape of ```(240,240,3)```.

You can also use neuralet with ROS. Since tflite runtime only supports python3, and ROS mainly works with python2 (although you can get it to work with python3 with some efforts), ```ros-server-example.py``` is modified to use ```pickle2reducer.py``` so the multiprocessing queue can work between python2 and python3. We also require converting the image from a ```np.ndarray``` to a python's native list for pickle to work properly.

ROS server uses the same container as above and runs ```ros-server-example.py``` to run the ROS server. ```ros-neuralet-bridge.py``` provides an example of using the server from a ROS node. It subscribes to an image topic and publishes the inference output on a result topic.

# Getting started:
There are two main ways to run this container. You can build the container from the Dockerfile or pull it from the Dockerhub.
## Build container from source:

```
# 1- Clone the repository
git clone https://github.com/neuralet/neuralet

# 2- Build the container
MODEL_NAME=efficientnet-edgetpu-M
cd neuralet/amd64/$MODEL_NAME
docker build -t "neuralet/amd64:$MODEL_NAME" .

# 3- Run the container
docker run -it --privileged --net=host -v $(pwd)/../../:/repo neuralet/amd64:$MODEL_NAME

# 4- Run inference on a test image
python3 src/client.py [PATH-TO-IMAGE]

# 5- Terminate the server and stop the container
python3 src/client.py stop
```

## Pull container from Dockerhub:

```
# 1- Clone the repository
git clone https://github.com/neuralet/neuralet

# 2- Run the container
MODEL_NAME=efficientnet-edgetpu-M
cd neuralet/amd64/$MODEL_NAME
docker run -it --privileged --net=host -v $(pwd)/../../:/repo neuralet/amd64:$MODEL_NAME

# 3- Run inference on a test image
python3 src/client.py [PATH-TO-IMAGE]

# 4- Terminate the server and stop the container
python3 src/client.py stop
```
## Run with ROS
Assuming you have ```ros-kinetic-perception``` or ```ros-melodic-perception``` installed on your ROS server, you can run the ROS example as below:

```
# 1- Clone the repository
git clone https://github.com/neuralet/neuralet

# 2- Run the container
MODEL_NAME=efficientnet-edgetpu-M
cd neuralet/amd64/$MODEL_NAME
docker run -it --privileged --net=host -v $(pwd)/../../:/repo --entrypoint="python3" neuralet/amd64:$MODEL_NAME src/ros-server-example.py

# 3- Start roscore
roscore

# 4- As an example, use image_publisher to publish your image continuesly:
rosrun image_publisher image_publisher __name:=publisher PATH_TO_IMAGE

# 5- get ready to monitor the output, on default result topic of ros-neuralet-bridge.py:
rostopic echo /result

# 6- Run the bridge which continuesly does the inference from publisher node's image topic, exit with Ctrl+C
# you can also change the result topic by adding "result:=/somename/sometopic" to the following command
python2 src/ros-neuralet-bridge.py image:=/publisher/image_raw

# 7- Terminate the server with Ctrl+C

```
