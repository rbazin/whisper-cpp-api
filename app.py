""" Flask app which transcribes audio files using whisper.cpp"""

from flask import Flask, request, jsonify
from flask_cors import CORS

import ffmpeg

import os
import subprocess

import logging
from time import time

app = Flask(__name__)
CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

def clear_files():
    for f in os.listdir(UPLOAD_FOLDER):
            os.remove(os.path.join(UPLOAD_FOLDER, f))

@app.route("/transcribe", methods=["POST"])
def transcribe():
    logging.info("Request received")
    clear_files()
    start = time()

    # verify method is POST
    if request.method != "POST":
        logging.error("Invalid request method")
        return jsonify({"error": "Invalid request method"}), 400
    
    if 'file' not in request.files:
        logging.error('No file part in the request')
        return jsonify({'error': 'No file part in the request'}), 400
    
    f = request.files['file']
    fname = f.filename
    if fname == '':
        logging.error('No file selected for transcription')
        return jsonify({'error': 'No file selected for transcription'}), 400
    

    logging.info('Saving file')
    f.save(os.path.join(UPLOAD_FOLDER, fname))
    logging.info('File saved')

    # TODO : check if its an audio file 
    # TODO : convert to wav if not wav
    if f.filename.split('.')[-1] != 'wav':
        logging.info("Converting to wav")
        try:
            input_stream = ffmpeg.input(os.path.join(UPLOAD_FOLDER, fname))
            output_stream = ffmpeg.output(input_stream, 
                                          os.path.join(UPLOAD_FOLDER, "audio.wav"), 
                                          format='wav', 
                                          ar='16000', 
                                          ac='1')
            ffmpeg.run(output_stream)
            fname = 'audio.wav'

        except Exception as e:
            logging.error(f"Error converting to wav : {str(e)}")
            return jsonify({"error": "Error while converting to wav", "status":"error"}), 500
        
        logging.info("Conversion successful")

    try:
        # INFO: using subprocess with whisper.cpp doesn't raise an error if the command fails
        logging.info("Transcribing audio")

        # create empty file to store transcript
        transcript_file = open(os.path.join(UPLOAD_FOLDER, f"transcript.txt"), "w")
        transcript_file.close()

        # transcribe the audio using whisper.cpp
        subprocess.run("./whisper.cpp/main \
                   -m ./whisper.cpp/models/ggml-base.bin \
                   -f {0} \
                   --output-file {1} \
                   --output-txt --language auto --no-timestamps".format(os.path.join(UPLOAD_FOLDER, "audio.wav"), os.path.join(UPLOAD_FOLDER, "transcript")), 
                   shell=True)
        
        logging.info("Transcription successful")

    except Exception as e:
        logging.error(f"Error transcribing audio : {str(e)}")
        return jsonify({"error": "Error while transcribing audio", "status":"error"}), 500

    try:
        logging.info("Reading transcript")

        # read and return the transcript from the file
        with open(os.path.join(UPLOAD_FOLDER, f"transcript.txt"), "r") as f:
            transcript = f.read()

        logging.info("Returning transcript")

        end = time()
        logging.info(f"Time to complete : {end-start:.2f}s")

        return jsonify({"transcript": transcript, "status":"success"}), 200
    
    except Exception as e:
        logging.error(f"Error reading transcript : {str(e)}")
        return jsonify({"error": "Error while reading transcript", "status":"error"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=4000, host="0.0.0.0")