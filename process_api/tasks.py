from celery import shared_task
from moviepy.editor import VideoFileClip, AudioFileClip
from io import BytesIO
from django.core.files.base import ContentFile

from .models import Video
from gradio_client import Client


@shared_task
def process_video(video_id, target_bitrate):
    video = Video.objects.get(pk=video_id)
    input_path = video.file.path
    output_path = f'processed_videos/{video_id}_processed.mp4'

    video_clip = VideoFileClip(input_path)
    processed_clip = video_clip.resize(width=640)

    # Write the processed video to a file
    processed_clip.write_videofile(output_path, format="mp4", bitrate=target_bitrate)

    # Save the processed video file path to the database
    video.processed_file = output_path
    video.save()

@shared_task
def extract_audio(video_id):
    video = Video.objects.get(pk=video_id)
    input_path = video.processed_file
    output_path = f'processed_videos/{video_id}_audio.wav'

    # Create an AudioFileClip from the processed video file
    audio_clip = AudioFileClip(input_path)

    # Save the audio to a separate file
    audio_clip.write_audiofile(output_path, codec='pcm_s16le', ffmpeg_params=["-ac", "1"])

    # Save the audio file path to the database
    video.audio_file = output_path
    video.save()

@shared_task
def transcribe_audio(video_id):
    video = Video.objects.get(pk=video_id)
    audio_path = video.audio_file

    # Read the audio file
    with open(audio_path, 'rb') as audio_file:
        audio_buffer = BytesIO(audio_file.read())

    client = Client("abidlabs/whisper")
    transcript = client.predict(audio_buffer)

    # Save the transcript to the database
    video.transcription = transcript
    video.save()

@shared_task
def update_video_transcription(video_id, transcript):
    video = Video.objects.get(pk=video_id)
    video.transcription = transcript
    video.save()
