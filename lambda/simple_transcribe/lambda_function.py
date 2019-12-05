from __future__ import print_function

import os
import json
import time
import boto3
import string
from random import *

import datetime
 
json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)

def lambda_handler(event, context):

    print("Event=" + json.dumps(event))
    sourceEvent = event['Records'][0]['s3']
    sourceBucket = sourceEvent['bucket']['name']
    sourceObject = sourceEvent['object']['key']
    

    job_uri = "https://s3-eu-west-1.amazonaws.com/" +  sourceBucket + "/" + sourceObject
    print("Processing source file=" + job_uri)
    
    # set default values
    languageCode = os.environ['LANGUAGE']
    customVocab = os.environ['CUSTOM_VOCABULARY'] + "_" + languageCode
    mediaFormat = 'mp4'
    
    suffixIndex = sourceObject.find('.', len(sourceObject)-6)
    if suffixIndex != -1 :
        mediaFormat = sourceObject[suffixIndex+1:]
        # accepted types formats: mp3 | mp4 | wav | flac
        if mediaFormat not in ['mp3', 'mp4', 'wav', 'flac'] :
                print("Unsupported media format=" + mediaFormat)
                return {
                    'statusCode': 500,
                    'body': "Unsupported media format='" + mediaFormat + "'. Media file extension should be either .mp3, .mp4, .wav or .flac"
                }
    else:
        print("Unknown file format, media file extension should be either .mp3, .mp4, .wav or .flac")
        return {
            'statusCode': 500,
            'body': "Unknown media format. Media file extension should be either .mp3, .mp4, .wav or .flac"
        }
        
    print("Expecting media format=" + mediaFormat)
    print("Expecting media language=" + languageCode)

    min_char = 8
    max_char = 12
    # allchar = string.ascii_letters + string.punctuation + string.digits
    allchar = string.ascii_letters + string.digits
    randomString = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
    job_name = "demo-transcribe"+randomString
    print("Starting Transcribe Job '" + job_name + "'")

    transcribe = boto3.client('transcribe')
    
    transcriptionJob = transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat=mediaFormat,
        LanguageCode=languageCode,
        Settings={
            "VocabularyName": customVocab,
            "MaxSpeakerLabels": 10,
            "ShowSpeakerLabels": True
        }
    )
    print("Transcription Job launched: " + json.dumps(transcriptionJob))
    
    return {
        'statusCode': 200,
        'body': json.dumps(transcriptionJob)
    }
