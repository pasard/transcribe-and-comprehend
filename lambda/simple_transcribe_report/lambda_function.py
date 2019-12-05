from __future__ import print_function

import os
import urllib.request
import json
import time
import boto3
import string
from random import *

import datetime
# import pyfpdf

json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)

def lambda_handler(event, context):
    # expecting Transcribe events for which TranscriptionJobStatus is either COMPLETED or FAILED
    # {
    #   "version": "0",
    #   "id": "999cccaa-eaaa-0000-1111-123456789012",
    #   "detail-type": "Transcribe Job State Change",
    #   "source": "aws.transcribe",
    #   "account": "123456789012",
    #   "time": "2016-12-16T20:57:47Z",
    #   "region": "us-east-1",
    #   "resources": [],
    #   "detail": {
    #     "TranscriptionJobName": "unique job name",
    #     "TranscriptionJobStatus": "COMPLETED"
    #     ]
    #   }
    # }

    print("Event=" + json.dumps(event))
    
    s3Bucket = os.environ['S3_BUCKET']
    sourceLanguage = os.environ['SOURCE_LANGUAGE']
    targetLanguage = os.environ['TARGET_LANGUAGE']

    transcribe = boto3.client('transcribe')
    job_name = event['detail']['TranscriptionJobName']
    job_report = transcribe.get_transcription_job(TranscriptionJobName=job_name)    
    print("Job report=" + json.dumps(job_report['TranscriptionJob']))

    status = event['detail']['TranscriptionJobStatus']
    statusCode = 200
    if status == 'COMPLETED':
        print("succesfully processed media file")
        transcriptFileUri = job_report['TranscriptionJob']['Transcript']['TranscriptFileUri']
        print("Transcript=" + transcriptFileUri)
        jsonurl = urllib.request.urlopen(transcriptFileUri)
        jsondata = json.loads(jsonurl.read().decode())
        print("Transcript data="+ json.dumps(jsondata))
        # further processing (eg call Amazon Comprehend) ...
        transcript = jsondata['results']['transcripts'][0]['transcript']
        print("Transcript="+ transcript)
        """ Transcript data=
        {
            "jobName": "kbc-testPo6SQzrXt03u",
            "accountId": "218077514144",
            "results": {
                "transcripts": [
                    {
                        "transcript": "donc vous? Notre raison d'être, c'est de fournir des ressources informatiques à nos clients. Et quand je dis ressources informatiques, c'est très vague. Ça va du serveur, de la base de données ou des services de plus haut niveau comme de d'intelligence artificielle pour reconnaît des images, reconnaît la parole et tous ses services. Les clients peuvent y accéder à travers des API. Donc tout ce qu'on fait chez vous, c'est une et Pia et on donne accès à nos services uniquement via des API. Donc les pieds est au coeur de ce qu'ont fait avant même d'en construire une console graphique. On construit d'abord une"
                    }
                ],
                "speaker_labels": {
                    "speakers": 1,
                    "segments": [
                        {
                            "start_time": "4.79",
                            "speaker_label": "spk_1",
                            "end_time": "38.5",
                            "items": [
                                {
                                    "start_time": "4.79",
                                    "speaker_label": "spk_1",
                                    "end_time": "5.04"
                                },
                                {
                                    "start_time": "5.04",
                                    "speaker_label": "spk_1",
                                    "end_time": "5.92"
                                },
                                {
                                    "start_time": "5.93",
                                    "speaker_label": "spk_1",
                                    "end_time": "6.76"
                                },
                                ...
                                {
                                    "start_time": "37.96",
                                    "speaker_label": "spk_1",
                                    "end_time": "38.5"
                                }
                            ]
                        }
                    ]
                },
                "items": [
                    {
                        "start_time": "4.79",
                        "end_time": "5.04",
                        "alternatives": [
                            {
                                "confidence": "1.0",
                                "content": "donc"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    {
                        "start_time": "5.04",
                        "end_time": "5.92",
                        "alternatives": [
                            {
                                "confidence": "0.635",
                                "content": "vous"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    {
                        "alternatives": [
                            {
                                "confidence": "0.0",
                                "content": "?"
                            }
                        ],
                        "type": "punctuation"
                    },
                    {
                        "start_time": "5.93",
                        "end_time": "6.76",
                        "alternatives": [
                            {
                                "confidence": "1.0",
                                "content": "Notre"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    ...
                    {
                        "start_time": "37.96",
                        "end_time": "38.5",
                        "alternatives": [
                            {
                                "confidence": "0.888",
                                "content": "une"
                            }
                        ],
                        "type": "pronunciation"
                    }
                ]
            },
            "status": "COMPLETED"
        } """
        transcript_html = "<head id='head'><title>Transcript demo for KBC</title> \
                            <meta name='description' content='' /> \
                            <meta http-equiv='content-type' content='text/html; charset=UTF-8' /> \
                            <meta name='theme-color' content='#009fda'> \
                            </head><body><font color='#009fda'><h1>Transcript report</h1></font> \
                            <h2>Transcript</h2>{}<hr/>".format(transcript)
        speakersNumber = jsondata['results']['speaker_labels']['speakers']
    
        transcript_html += "<h2>Number of speakers detected: {}</h2>".format(speakersNumber)
        
        # show split per speaker if more than one speaker
        if speakersNumber > 1:
            transcript_html += "<h2>Transcript details: </h2><br/> \
                                    <table border='1' style='table-layout: fixed; width: 100%'> \
                                    <tr> \
                                        <th style='width: 10%;'>Speaker</th> \
                                        <th>Text</th> \
                                    </tr>"
            
            # a segment contains the start and end times and the speaker #
            segments = jsondata['results']['speaker_labels']['segments']
            """
            a Segment is made like this :
            { 
                "start_time": "4.79",
                "speaker_label": "spk_0",
                "end_time": "38.5",
                "items": [
                    {
                        "start_time": "4.79",
                        "speaker_label": "spk_0",
                        "end_time": "5.04"
                    },
                    ...
                    {
                        "start_time": "23.96",
                        "speaker_label": "spk_0",
                        "end_time": "24.5"
                    },
                ]
            },
            {
                "start_time": "24.7",
                "speaker_label": "spk_1",
                "end_time": "82.26",
                "items": [
                    {
                        "start_time": "24.7",
                        "speaker_label": "spk_1",
                        "end_time": "25.04"
                    },
                    ...
                    {
                        "start_time": "81.91",
                        "speaker_label": "spk_1",
                        "end_time": "82.26"
                    }
                ]
            },
            """
            items = jsondata['results']['items'] 
            # an item contains the start and end times and the content
            """
            an Item can be either this :
            {
                "start_time": "5.04",
                "end_time": "5.92",
                "alternatives": [
                    {
                        "confidence": "0.635",
                        "content": "vous"
                    }
                ],
                "type": "pronunciation"
            } 
            or that (for punctuations w/o times info) :
            {
                "alternatives": [
                    {
                        "confidence": "0.0",
                        "content": "?"
                    }
                ],
                "type": "punctuation"
            },
            
            """
            segment_idx = 0
            item_idx = 0
            item_end_time = ''
            # loop through all segments
            for segment in segments:
                speaker_label = segments[segment_idx]['speaker_label']
                segment_start_time = segments[segment_idx]['start_time']
                segment_end_time = segments[segment_idx]['end_time']
                print("Speaker label={}, Start Time={}, End Time={}".format(speaker_label, segment_start_time, segment_end_time))
                speaker_text = ''
    
                # loop through all the items in parallel
                print("Number of items={}".format(len(items)))
                while item_idx < len(items):
                    speaker_text += items[item_idx]['alternatives'][0]['content']
                    if items[item_idx]['type'] != "punctuation":
                        speaker_text += ' '
                        if items[item_idx]['end_time'] == segment_end_time:
                            if items[item_idx+1]['type'] == "punctuation":
                                speaker_text += items[item_idx+1]['alternatives'][0]['content']
                                item_idx += 2
                            break
    
                        print("Segment#{}, Item#{}, segment_end_time={}, index_end_time={}, speaker text={}".format(segment_idx, item_idx, segment_end_time, items[item_idx]['end_time'], speaker_text))
                    item_idx += 1
                    
                transcript_html += "<tr> \
                                        <td>Speaker #{}</th> \
                                        <td style='word-wrap: break-word'>{}</th> \
                                    </tr>".format(str(int(speaker_label[-1])), speaker_text)
                print("Segment#{}, Item#{}, HTML=".format(segment_idx, item_idx, transcript_html))
                segment_idx += 1
                
    
            """ TABLE
                <table border="1">
                <tr>
                <th>Header 1</th>
                <th>Header 2</th>
                </tr>
                <tr>
                <td>Cell A1</td>
                <td>Cell B1</td>
                </tr>
                <tr>
                <td>Cell A2</td>
                <td>Cell B2</td>
                </tr>
                </table>
            """
            transcript_html += "</table><hr/>"
        
        print("HTML output=" + transcript_html)
        
        # Translate back to English for Comprehend if needed
        target_transcript = transcript
        if sourceLanguage != targetLanguage:
            translate = boto3.client('translate')
            first5k = transcript
            if len(transcript) > 5000:
                # Translate text limit set to 5kB
                first5k = transcript[:4500] + "[...]"
            result = translate.translate_text(Text=first5k, 
                SourceLanguageCode=sourceLanguage, TargetLanguageCode=targetLanguage)
            target_transcript = result.get('TranslatedText')
            print('TranslatedText: ' + target_transcript)
            print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
            print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))
            transcript_html += '<h2>Translated Text</h2>'
            transcript_html += target_transcript + '<hr/>'
    
        # use Comprehend to analyze the text for sentiment, entities and key phrases
        comprehend = boto3.client('comprehend')
        kpData = comprehend.detect_key_phrases(Text=target_transcript, LanguageCode=targetLanguage)
        print("key Phrases=" + json.dumps(kpData))
        enData = comprehend.detect_entities(Text=target_transcript, LanguageCode=targetLanguage)
        print("Entities=" + json.dumps(enData))
        snData = comprehend.detect_sentiment(Text=target_transcript, LanguageCode=targetLanguage)
        print("Sentiment=" + json.dumps(snData))
    
        transcript_html += '<h2>Transcript Analysis</h2>'
        transcript_html += '<h3>Sentiment</h3>'
        transcript_html += '<b><font color="#009fda">{}</font></b>'.format(snData['Sentiment'])
    
        transcript_html += '<hr/><h3>Key Phrases</h3> \
                            <ul>'
        for keyPhrase in kpData['KeyPhrases']:
            transcript_html += '<li>{}</li>'.format(keyPhrase['Text'])
        transcript_html += '</ul>'
    
        transcript_html += "<hr/><h3>Entities: </h3> \
                                <table border='1' style='table-layout: fixed; width: 30%'> \
                                <tr> \
                                    <th style='width: 40%;'>Type</th> \
                                    <th>Text</th> \
                                </tr>"
        for entity in enData['Entities']:
            transcript_html += "<tr> \
                                    <td>{}</th> \
                                    <td style='word-wrap: break-word'>{}</th> \
                                </tr>".format(entity['Type'], entity['Text'])
        transcript_html += "</table><hr/>"
    
        transcript_html += "</body>"
    
        s3 = boto3.client("s3")
        response = s3.put_object(
            Body=transcript_html,
            Bucket=s3Bucket,
            # Key='output/' + job_name + '.html',
            Key=job_name + '.html',
            Metadata={
                'report': 'Transcript output and text analysis for media -{}-'.format(job_report['TranscriptionJob']['Media']['MediaFileUri'])
            })
            
#        pdf = pyfpdf.FPDF(format='A4')
#        pdf.add_page()
#        pdf.set_font("Arial", size=12)
#        pdf.cell(200, 10, txt="Welcome to Python!", align="C")
#        pdf.output("test.pdf")
#        s3.upload_fileobj("test.pdf", S3_BUCKET, "output/" + job_name + ".pdf")
        
    else:
        statusCode = 500
        response = '<h1>ERROR</h1>'
        if status == 'FAILED':
            print("Failed processing media file")
        else:
            print("Unexpected status captured=" + status)


    return {
        'statusCode': statusCode,
        # 'body': json.dumps(job_report['TranscriptionJob'])
        'body': response
    }
