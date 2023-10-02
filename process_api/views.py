from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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

    # Assume 'chunk' is a key in the request data that contains the chunk data
    chunk_data = request.data.get('chunk')
    
    # Save the chunk to a file
    chunk_path = f'video_chunks/{video_id}_{request.data.get("chunk_number")}.mp4'
    with open(chunk_path, 'wb') as chunk_file:
        chunk_file.write(chunk_data)

    # Update the video object to keep track of uploaded chunks
    video.uploaded_chunks += 1
    video.save()

    return Response({'message': 'Chunk uploaded successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def stop_recording(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Trigger the video processing task if all chunks have been uploaded
    if video.uploaded_chunks == video.total_chunks:
        process_video.delay(video.id)

    return Response({'message': 'Recording stopped.'}, status=status.HTTP_200_OK)

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

    transcribe_audio.delay(video.id)  # Trigger the transcription task asynchronously

    return Response({'message': 'Transcription process started.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_transcription(request, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'transcription': video.transcription}, status=status.HTTP_200_OK)
