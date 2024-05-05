import json
from pytube import YouTube
import boto3
from moviepy.editor import AudioFileClip
from transformers import pipeline
from loguru import logger
from random_word import RandomWords

queue_name = 'khader-youtube-jobs'

sqs_client = boto3.client('sqs', region_name='eu-west-3')


def consume():
    while True:
        response = sqs_client.receive_message(QueueUrl=queue_name, MaxNumberOfMessages=1, WaitTimeSeconds=5)

        if 'Messages' in response:
            message = response['Messages'][0]['Body']
            receipt_handle = response['Messages'][0]['ReceiptHandle']
            msg_id = response['Messages'][0]['MessageId']

            print("Received message:", message)

            try:
                # yt = YouTube(message)
                # audio_stream = yt.streams.filter(only_audio=True).first()
                # filename = yt.title.replace(' ', '_') + '.mp4'
                # audio_stream.download(filename=filename)

                # audio = AudioFileClip(filename)
                # audio.write_audiofile(filename + '.flac', codec='flac')

                # filename = filename + '.flac'
                # result = generator(filename)
                r = RandomWords()
                textFromSpeech = ""
                for i in range(50):
                    textFromSpeech += r.get_random_word()
                    textFromSpeech += " "    
                logger.info(f'Results for job{msg_id} is:\n{textFromSpeech}')

                #write result to DynamoDB
                try: 
                    dynamodb = boto3.resource('dynamodb')
                    table = dynamodb.Table('khader-speechText')
                    table.put_item(Item={
                        "jobID": msg_id ,
                        "textFromSpeech": textFromSpeech
                    })
                    logger.info("Item saved successfully!")
                    sqs_client.delete_message(QueueUrl=queue_name, ReceiptHandle=receipt_handle)
                except Exception as e:
                    logger.info(f"couldn't save item in DynamoDB due to {e}")

            except Exception as e:
                logger.error(str(e))


if __name__ == '__main__':
    generator = pipeline(model="openai/whisper-tiny")
    consume()