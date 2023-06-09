#FROM jupyter/tensorflow-notebook:5b2160dfd919
#FROM tensorflow/tensorflow:1.6.0-py3
#FROM tensorflow/tensorflow:1.11.0-gpu-py3
FROM tensorflow/tensorflow:1.13.2-gpu-py3-jupyter
RUN pip install --upgrade pip
RUN python -m pip install -U matplotlib==2.1.0
RUN pip install pandas
RUN python -m pip install scikit-learn
RUN python -m pip install scipy
RUN python -m pip install svgwrite
RUN pip install xmltodict

RUN rm /etc/apt/sources.list.d/cuda.list
RUN rm /etc/apt/sources.list.d/nvidia-ml.list
RUN apt-key del 7fa2af80
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

RUN apt-get update

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Edmonton
RUN apt-get install -y python3-tk


#RUN apt-get install python3-tk