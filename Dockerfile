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
RUN apt-get update
RUN apt-get install python3-tk

#RUN apt-get install python3-tk