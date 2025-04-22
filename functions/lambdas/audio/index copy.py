import json
import base64
import boto3
import wave
import time  # Add import for time

_cache = {}
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Loop through the records in the event
    print(json.dumps(event))
    updated_ids = set()  # Track updated cache items
    for record in event['Records']:
        try:
            # Decode the base64-encoded Kinesis data
            kinesis_data = base64.b64decode(record['kinesis']['data'])
            id = record['kinesis']['partitionKey']
            sanitized_id = ''.join(e for e in id if e.isalnum() or e in ('-', '_'))  # Remove special characters
            
            # Append kinesis_data to _cache for the given id
            if id not in _cache:
                _cache[id] = b''  # Initialize as an empty bytes object
            _cache[id] += kinesis_data  # Concatenate bytes
            updated_ids.add(id)  # Mark this id as updated

            print(f"Processed data for ID: {id}")
        except Exception as e:
            print(f"[ERROR] Failed to process record: {str(e)}")
            continue  # Skip to the next record

    # Upload updated cache items to S3
    for id in updated_ids:
        #try:
            sanitized_id = ''.join(e for e in id if e.isalnum() or e in ('-', '_'))[:200]  # Remove special characters and truncate to 200 characters
            s3_key = f"audio/{sanitized_id}.wav"  # Define the S3 object key
            s3_key_s = f"scripts/{sanitized_id}.wav"  # Define the S3 object key
            s3_bucket = "dmh-prod1-deploy-bucket"  # Replace with your S3 bucket name
            sample_width = 2         # 16-bit PCM = 2 bytes
            num_channels = 1         # Mono
            sample_rate = 44100      # 16 kHz

            # Output WAV file
            output_filename = f'/tmp/{id}.wav'
            binary_data = _cache[id]
            with wave.open(output_filename, 'wb') as wav_file:
                wav_file.setnchannels(num_channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(binary_data)
            
        #     print(f'WAV file saved as {output_filename}')
        #     with open(output_filename, 'rb') as wav_file:
        #         s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=wav_file)

        #     print(f"Uploaded WAV file for ID: {id}")

        #     # Transcribe the uploaded file
        #     transcribe = boto3.client('transcribe')
        #     job_name = f"transcription_{sanitized_id}_{int(time.time())}"
        #     transcribe.start_transcription_job(
        #         TranscriptionJobName=job_name,
        #         Media={'MediaFileUri': f's3://{s3_bucket}/{s3_key}'},
        #         MediaFormat='wav',
        #         LanguageCode='en-US'
        #     )
        #     print(f"Started transcription job: {job_name}")

        #     # Wait for the transcription job to complete
        #     while True:
        #         status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        #         if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        #             break
        #         print(f"Waiting for transcription job {job_name} to complete...")
        #         time.sleep(2)

        #     if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        #         transcription_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        #         print(f"Transcription completed. Retrieving result from: {transcription_url}")

        #         # Retrieve transcription result from the URL
        #         transcription_result = boto3.client('s3').get_object(Bucket=s3_bucket, Key=transcription_url.split('?')[-1])
        #         print(transcription_result)
        #         transcription_content = transcription_result['Body'].read().decode('utf-8')

        #         # Save transcription result to S3
        #         transcription_s3_key = s3_key_s
        #         s3.put_object(Bucket=s3_bucket, Key=transcription_s3_key, Body=transcription_content)
        #         print(f"Transcription result saved to S3: {transcription_s3_key}")
        #     else:
        #         print(f"[ERROR] Transcription job {job_name} failed.")

        # except Exception as e:
        #     print(f"[ERROR] Failed to upload or transcribe WAV file for ID {id}: {str(e)}")
        #     continue  # Skip to the next item

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Kinesis data processed successfully"})
    }


import asyncio
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import AudioEvent

REGION = "us-east-1"
LANGUAGE_CODE = "en-US"
SAMPLE_RATE = 44100


class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event):
        results = transcript_event.transcript.results
        for result in results:
            if result.alternatives:
                transcript = result.alternatives[0].transcript
                if transcript:
                    print(f"Transcript: {transcript}")

async def stream_audio(audio_source_generator, id=None):
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

# Dummy audio source for example (replace this with Kinesis, WebSocket, etc.)
async def dummy_audio_generator():
    with open("example.raw", "rb") as f:  # PCM-encoded 16kHz, 16-bit mono audio
        while chunk := f.read(3200):  # Approx. 100ms of audio
            yield chunk
            await asyncio.sleep(0.1)

# Run the streaming loop
#if __name__ == "__main__":
#    asyncio.run(stream_audio(dummy_audio_generator()))
