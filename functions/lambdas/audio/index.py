import json
import base64
import boto3
import wave
import time  # Add import for time
import datetime
import asyncio
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import AudioEvent

import boto3
import base64
from collections import defaultdict

kinesis = boto3.client("kinesis")
stream_name = "YourStreamName"

_cache = {}
_clients = {}
s3 = boto3.client('s3')
SESSION_CHUNKS = defaultdict(list)

def lambda_handler(event, context):
    # Loop through the records in the event
    print(json.dumps(event))
    updated_ids = set()  # Track updated cache items
        

    for record in event['Records']:
        data = base64.b64decode(record['data'])
        session_id = record['PartitionKey']
        SESSION_CHUNKS[session_id].append(data)

    asyncio.run(transcribe_from_kinesis_shard(session_id, SESSION_CHUNKS[session_id]))
        
    while SESSION_CHUNKS.get(session_id,'') != '':
        time.sleep(5)  # Wait to complete the transcription
        print(f"Waiting for transcription to complete for session ID: {session_id}")


    print(f"Transcription completed for session ID: {session_id}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Kinesis data processed successfully"})
    }






REGION = "eu-west-1-east-1"
LANGUAGE_CODE = "en-US"
SAMPLE_RATE = 44100
BUCKET_NAME = "dmh-prod1-deploy-bucket"

class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event):
        results = transcript_event.transcript.results
        for result in results:
            if result.alternatives:
                transcript = result.alternatives[0].transcript
                if transcript:
                    print(f"Transcript: {transcript}")

async def stream_audio(audio_source_generator):
    client = TranscribeStreamingClient(region=REGION)

    # Start transcription stream
    stream = await client.start_stream_transcription(
        language_code=LANGUAGE_CODE,
        media_sample_rate_hz=SAMPLE_RATE,
        media_encoding="pcm"
    )

    handler = MyEventHandler(stream.output_stream)

    async def write_chunks():
        async for chunk in audio_source_generator:
            audio_event = AudioEvent(audio_chunk=chunk)
            await stream.input_stream.send_audio_event(audio_event)
        await stream.input_stream.end_stream()

    await asyncio.gather(write_chunks(), handler.handle_events())




def get_audio_chunks():
    shard_id = kinesis.describe_stream(StreamName=stream_name)['StreamDescription']['Shards'][0]['ShardId']
    shard_it = kinesis.get_shard_iterator(StreamName=stream_name,
                                          ShardId=shard_id,
                                          ShardIteratorType='TRIM_HORIZON')['ShardIterator']
    
    session_chunks = defaultdict(list)

    while True:
        out = kinesis.get_records(ShardIterator=shard_it, Limit=100)
        shard_it = out['NextShardIterator']

        for record in out['Records']:
            data = base64.b64decode(record['Data'])
            session_id = record['PartitionKey']
            session_chunks[session_id].append(data)

        if len(session_chunks):
            for session_id, chunks in session_chunks.items():
                asyncio.run(transcribe_from_kinesis_shard(session_id, chunks))
            session_chunks.clear()


class TranscriptCollector(TranscriptResultStreamHandler):
    def __init__(self, output_stream, session_id):
        super().__init__(output_stream)
        self.session_id = session_id
        self.transcripts = []

    async def handle_transcript_event(self, transcript_event):
        for result in transcript_event.transcript.results:
            if result.alternatives:
                transcript = result.alternatives[0].transcript
                if transcript:
                    self.transcripts.append(transcript)
                    print(f"[{self.session_id}] Transcript: {transcript}")

    def save_to_s3(self):
        content = "\n".join(self.transcripts)
        filename = f"{self.session_id}-{datetime.utcnow().isoformat()}.txt"
        s3.put_object(Bucket=BUCKET_NAME, Key=f"transcribe/{filename}", Body=content.encode("utf-8"))
        print(f"[{self.session_id}] Transcript saved to s3://{BUCKET_NAME}/transcribe/{filename}")

async def transcribe_from_kinesis_shard(session_id, audio_chunks):
    client = TranscribeStreamingClient(region=REGION)

    stream = await client.start_stream_transcription(
        language_code=LANGUAGE_CODE,
        media_sample_rate_hz=SAMPLE_RATE,
        media_encoding="pcm"
    )

    handler = TranscriptCollector(stream.output_stream, session_id)

    async def write_chunks():
        while len(SESSION_CHUNKS.get(session_id)) > 0:
            chunk = SESSION_CHUNKS[session_id].pop(0)
            audio_event = AudioEvent(audio_chunk=chunk)
            await stream.input_stream.send_audio_event(audio_event)
            await asyncio.sleep(0.2)  # simulate real-time pacing
        await stream.input_stream.end_stream()

    await asyncio.gather(write_chunks(), handler.handle_events())
    handler.save_to_s3()
    print(f"[{session_id}] Transcription completed and saved to S3.")
    del SESSION_CHUNKS[session_id]  # Clear the session chunks after processing

