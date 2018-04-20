FROM tensorflow/tensorflow:latest-gpu-py3

RUN apt update && apt install -y curl \
    && echo "Pulling watchdog binary from Github." \
    && curl -sSLf https://github.com/openfaas-incubator/of-watchdog/releases/download/0.2.3/of-watchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog

# Object detection - Start
COPY requirements.txt   .
RUN pip install -r requirements.txt

RUN apt update && apt install -y git \
    && apt install -y vim-nox \
    && apt install -y python3-tk \   
    && curl -OL https://github.com/google/protobuf/releases/download/v3.5.1/protoc-3.5.1-linux-x86_64.zip \
    && unzip protoc-3.5.1-linux-x86_64.zip -d protoc3 \
    && mv protoc3/bin/* /usr/local/bin/ \
    && mv protoc3/include/* /usr/local/include/
    #&& apt install -y protobuf-compiler

WORKDIR /root/
RUN git clone https://github.com/tensorflow/models

RUN git clone https://github.com/cocodataset/cocoapi \
    && cd cocoapi/PythonAPI \
    && make install

WORKDIR /root/models/research
ENV PYTHONPATH $PYTHONPATH:/root/models/research/:/root/models/research/slim
RUN protoc object_detection/protos/*.proto --python_out=.
WORKDIR /root/models/research/object_detection

COPY settings.py .
COPY download_model.py .
RUN python3 download_model.py
COPY index.py .
# Object detetion - End


RUN mkdir -p function
RUN touch ./function/__init__.py
COPY function           function

ENV fprocess="python index.py"
ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"


HEALTHCHECK --interval=1s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
