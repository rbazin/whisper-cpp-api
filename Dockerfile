FROM python:3.11.2-slim

# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED TRUE

# install system dependencies
RUN apt-get update \
    && apt-get -y install gcc make wget git ffmpeg g++ \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --no-cache-dir --upgrade pip

# set work directory
WORKDIR /app

# copy requirements.txt
COPY ./requirements.txt /app/requirements.txt

# install project requirements
RUN pip install --no-cache-dir -r requirements.txt
RUN git clone https://github.com/ggerganov/whisper.cpp.git -b v1.2.1
RUN cd whisper.cpp && /bin/bash ./models/download-ggml-model.sh base && make

# copy project
COPY . .

# set app port
EXPOSE 4000

# Run app.py when the container runs
CMD ["gunicorn"  , "-b", "0.0.0.0:4000", "-t", "600", "app:app"] 
