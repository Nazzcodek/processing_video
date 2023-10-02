from django.db import models

class Video(models.Model):
    file = models.FileField(upload_to='uploads/')
    processed_clips = models.JSONField(default=list)  # List to store paths of processed chunks
    final_video = models.FileField(upload_to='final_videos/', blank=True, null=True)
    transcription = models.TextField(blank=True, null=True)
    uploaded_chunks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
