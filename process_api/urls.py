from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import start_recording, upload_chunk, stop_recording, process_status

urlpatterns = [
    path('start_recording/', start_recording, name='start_recording'),
    path('upload_chunk/<int:video_id>/', upload_chunk, name='upload_chunk'),
    path('stop_recording/<int:video_id>/', stop_recording, name='stop_recording'),
    path('process_status/<int:video_id>/', process_status, name='process_status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
