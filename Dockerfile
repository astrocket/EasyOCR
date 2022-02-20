FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

# Configure apt and install packages
RUN apt-get update -y && \
    apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    git \
    # cleanup
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/li

RUN pip install easyocr \
    opencv-python-headless==4.5.4.60 \
    flask \
    flask_limiter \
    image \
    pillow \
    waitress

ENV ROOT $HOME/.EasyOCR
RUN mkdir $ROOT
WORKDIR $ROOT

COPY . .

EXPOSE 8000

CMD python3 app.py