# Processing video API
This is a Django-based backend implementation for a screen recording web app. The web app allows users to record their screen, and the backend processes the recorded video, extracts audio, transcribes it, and returns the processed video along with the transcript.

# Features
- Start Recording: Initiates the screen recording process.
- Upload Chunk: Handles the uploading of video chunks in real-time.
- Stop Recording: Signals the end of recording and triggers video processing.
- Process Status: Retrieves the processing status of a video.
- Start Transcription: Initiates the audio transcription process.
- Get Transcription: Retrieves the transcription of a video.
- Get Processed video: Retrieves the processed video.

## Installation
1. Clone the repository: 

`git clone https://github.com/your-username/screen-recording-app.git` 

`cd processing_video`

2. Install dependencies:

`pip install -r requirements.txt`

3. Run migrations:

`python manage.py migrate`

4. Start the Django development server:

`python manage.py runserver`

`Visit [processing-video](https://www.processing-video.onrender.com) for documentation

Usage Start the screen recording from the frontend. Chunks of the recording are sent to the backend in real-time. Stop the recording to trigger video processing. Retrieve the processed video and transcription. Contributing Feel free to contribute to the project by opening issues or submitting pull requests. Make sure to follow the contribution guidelines.

License This project is licensed under the MIT License.

Replace placeholders such as `https://github.com/your-username/processing_video-a`