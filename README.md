# Whisper.cpp Docker API

A Whisper API than can be deployed instantly using Docker. Entirely based on [whisper.cpp](https://github.com/ggerganov/whisper.cpp), which enables running whisper on consumer-grade CPU.

**Note** : This is still an early version of the docker API, mainly made for myself. Feel free to use it and improve it as you want.

## Usage

To use this repo, you will need to have the docker engine installed and running.

First, build the image from the root folder :

```bash
docker build -t whisper .
```

Then, run the container :

```bash
docker run --rm -d -p 4000:4000 --name whisper whisper:latest
```

To see if the API is working properly, you can use the following request :

```bash
curl -X POST \
    -H "Content-Type: multipart/form-data" \
    -F "file=@./audio_file.mp3" http://localhost:4000/transcribe
```

The API actually works with all types of audio files and will handle converting them to the right format (.wav).

The API is fast, still there's a timeout set to 600s in the docker file, which can be reached for exceptionnally large files. By default, the API will kill the worker and return nothing.

## Using different whisper models

By default, the API is using the "base" model shize for whisper. If you have a good CPU, it could be interesting to increase the size of the model used in order to improve the transcription quality.

Both the `Dockerfile` and the `app.py` script have to be changed in order to use another size.