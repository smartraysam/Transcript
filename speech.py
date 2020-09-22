from google.cloud import storage
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import wave

import io
import re
import pathlib
import os

_path = os.getcwd()
output_filepath = _path + "\\transcript"
audio_file_name = ""


def google_transcribe():

    creditialpath = _path + "/speech.json"
    print(creditialpath)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creditialpath
    bucket_name = "speechtransfiv"
    # source_file_name = base_dir +"/"+ audio_file_name

    # destination_blob_name = audio_file_name

    # upload_blob(bucket_name, source_file_name, destination_blob_name)

    files = list_files(bucket_name)
    if len(files) == 0:
        print("No file in storage. please upload file")
        return
    for blob in files:
        print(blob)
        audio_file_name = blob
        gcs_uri = "gs://speechtransfiv/" + audio_file_name
        transcript = ""

        client = speech.SpeechClient()
        audio = types.RecognitionAudio(uri=gcs_uri)

        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=48000,
            audio_channel_count=2,
            language_code="es-CL",
            enable_separate_recognition_per_channel=True,
        )

        # Detects speech in the audio file
        operation = client.long_running_recognize(config, audio)
        response = operation.result(timeout=50000)

        for result in response.results:
            transcript += result.alternatives[0].transcript

        # print(transcript)
        transcript_filename = audio_file_name.split(".")[0] + ".txt"
        write_transcripts(transcript_filename, transcript)
        print("Transcript Done!!!")
        delete_blob(bucket_name, audio_file_name)
    print("All Files Transcripting Finish")


def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)


def write_transcripts(transcript_filename, transcript):
    f = open(output_filepath + "/" + transcript_filename, "w+")
    f.write(transcript)
    f.close()


def list_files(bucket_name):
    """List all files in GCP bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    files = bucket.list_blobs()
    fileList = [file.name for file in files if "." in file.name]
    return fileList


google_transcribe()
