FROM pytorch/pytorch

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

RUN pip install opencv-contrib-python-headless \
    easyocr \
    flask \
    flask_limiter \
    image \
    pillow \
    git+git://github.com/jaidedai/easyocr.git

ENV ROOT /app

RUN mkdir $ROOT
WORKDIR $ROOT

COPY . .

EXPOSE 8000

CMD python3 app.py