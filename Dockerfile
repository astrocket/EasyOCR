FROM wookbyung/easyocrmodel AS build
FROM pytorch/pytorch

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update
RUN apt-get install -y libsm6 libxext6 libxrender-dev libgl1-mesa-glx

RUN apt-get update && apt-get -y install libglib2.0-0; apt-get clean
RUN pip install opencv-contrib-python-headless

RUN pip install easyocr
RUN pip install git+git://github.com/jaidedai/easyocr.git
RUN pip install flask
RUN pip install flask_limiter
RUN pip install image
RUN pip install pillow

COPY . .

RUN echo $HOME


RUN mkdir $HOME/.EasyOCR
RUN mkdir $HOME/.EasyOCR/model
COPY --from=build /root/models/ /root/.EasyOCR/model/
# COPY ./model/* $HOME/.EasyOCR/model/
# RUN ls $HOME/.EasyOCR/model
# RUN mv ./model/* $HOME/.EasyOCR/model/
# RUN ls $HOME/.EasyOCR/model


EXPOSE 8000

CMD python3 app_gpu.py