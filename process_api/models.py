from django.db import models

class Video(models.Model):
    file = models.FileField(upload_to='uploads/')
    processed_file = models.FileField(upload_to='processed_videos/', blank=True, null=True)
    audio_file = models.FileField(upload_to='processed_videos/', blank=True, null=True)
    transcription = models.TextField(blank=True, null=True)
    uploaded_chunks = models.IntegerField(default=0)
    total_chunks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
