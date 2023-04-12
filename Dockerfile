FROM debian:11 AS build

RUN apt -q -y update && apt -q -y upgrade
RUN apt -q -y install -q -y libsdl2-dev alsa-utils
RUN apt -q -y install -q -y g++ make wget git

RUN git clone --depth 1 https://github.com/ggerganov/whisper.cpp.git -b v1.2.1

WORKDIR /whisper.cpp

ARG model=base
RUN bash ./models/download-ggml-model.sh "${model}"
RUN make main

# second stage for image optimization
FROM python:3.11-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# set work directory
WORKDIR /app

ARG model=base
RUN mkdir -p /app/whisper.cpp/models
COPY --from=build "/whisper.cpp/models/ggml-${model}.bin" "/app/whisper.cpp/models/ggml-${model}.bin"
COPY --from=build /whisper.cpp/main /app/whisper.cpp/

# install dependencies
RUN pip install --no-cache-dir --upgrade pip

# copy requirements.txt
COPY ./requirements.txt /app/requirements.txt

# install project requirements
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# expose port and run server
EXPOSE 4000
CMD ["gunicorn"  , "-b", "0.0.0.0:4000", "-t", "600", "app:app"] 
