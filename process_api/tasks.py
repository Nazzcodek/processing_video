from celery import shared_task
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
from io import BytesIO
import os
from .models import Video
from gradio_client import Client 

@shared_task
def process_video(video_id, chunk_path):
    video = Video.objects.get(pk=video_id)

    # Process the current chunk
    chunk_clip = VideoFileClip(chunk_path)
    processed_clip = chunk_clip.resize(width=640)

    # Save the processed chunk
    processed_chunk_path = f'processed_chunks/{video_id}_{video.uploaded_chunks}_processed.mp4'
    processed_clip.write_videofile(processed_chunk_path, format="mp4", codec="libx264", audio_codec="aac")

    # Add the processed chunk to the list
    video.processed_clips.append(processed_chunk_path)
    video.save()

    # Clean up: Delete the processed chunk file
    os.remove(processed_chunk_path)

@shared_task
def compile_final_video(video_id):
    video = Video.objects.get(pk=video_id)

    # Concatenate all processed chunks to build the final video
    final_video_path = f'final_videos/{video_id}_final.mp4'
    concatenate_videoclips([VideoFileClip(chunk) for chunk in video.processed_clips]).write_videofile(
        final_video_path, format="mp4", codec="libx264", audio_codec="aac"
    )

    # Save the path of the final video in the database
    video.final_video = final_video_path
    video.save()

    
@shared_task
def transcribe_audio(video_id):
    video = Video.objects.get(pk=video_id)
    audio_path = video.final_video  # Use the final processed video for transcription

    # Read the audio from the final processed video
    with VideoFileClip(audio_path) as final_clip:
        final_audio = final_clip.audio

        # Fade in and fade out audio
        final_audio_faded = audio_fadein(audio_fadeout(final_audio, final_clip.duration - 1), 1)

        # Save the audio to a separate file
        audio_buffer = BytesIO()
        final_audio_faded.write_audiofile(audio_buffer, codec='pcm_s16le', ffmpeg_params=["-ac", "1"])
        audio_buffer.seek(0)

    client = Client("abidlabs/whisper")
    transcript = client.predict(audio_buffer)

    # Save the transcript to the database
    video.transcription = transcript
    video.save()
