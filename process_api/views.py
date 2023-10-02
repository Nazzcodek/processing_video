from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.http import JsonResponse

from .models import Video
from .tasks import process_video, transcribe_audio
from .serializers import VideoSerializer

@api_view(['POST'])
def start_recording(request):
    serializer = VideoSerializer(data=request.data)
    if serializer.is_valid():
        video = serializer.save()
        return Response({'message': 'Recording started.', 'video_id': video.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def upload_chunk(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

    chunk_data = request.data.get('chunk')
    
    # Save the chunk to a file
    chunk_path = f'video_chunks/{video_id}_{request.data.get("chunk_number")}.mp4'
    with open(chunk_path, 'wb') as chunk_file:
        chunk_file.write(chunk_data)

    # Update the video object to keep track of uploaded chunks
    video.uploaded_chunks += 1
    video.save()

    # Process the current chunk in real-time
    process_video.delay(video.id, chunk_path)

    return Response({'message': 'Chunk uploaded successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def stop_recording(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if a certain duration of inactivity has passed (adjust the threshold as needed)
    if has_inactivity_passed(video, threshold_minutes=15):
        # Trigger the video processing task
        process_video.delay(video.id)

        return JsonResponse({'message': 'Recording stopped. Video processing initiated.'}, status=status.HTTP_200_OK)

    return JsonResponse({'message': 'Recording stopped.'}, status=status.HTTP_200_OK)


def has_inactivity_passed(video, threshold_minutes):
    if video.updated_at:
        time_since_last_chunk = datetime.now() - video.updated_at
        return time_since_last_chunk > timedelta(seconds=threshold_minutes)
    return False


@api_view(['GET'])
def process_status(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = VideoSerializer(video)
    return Response(serializer.data)

@api_view(['POST'])
def start_transcription(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

    transcribe_audio.delay(video.id)
    return Response({'message': 'Transcription process started.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_transcription(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'transcription': video.transcription}, status=status.HTTP_200_OK)
