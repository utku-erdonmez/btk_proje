from moviepy.editor import VideoFileClip
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor
from pytubefix import YouTube
import os

# Ensure the temporary directory exists
os.makedirs("./temp", exist_ok=True)
temp_dir = './temp'

# Function to download the video and extract audio, then return the audio file path
def download_and_extract_audio_then_return_audio_path(input_source): 
    yt = YouTube(input_source)
    video_file = os.path.join(temp_dir, f'{yt.video_id}.mp4')
    
    # If the video is already downloaded, do not download it again
    if not os.path.exists(video_file):
        try:
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path=temp_dir, filename=os.path.basename(video_file))
            print("Video downloaded successfully!")
        except Exception as e:
            return f"Error downloading video: {e}"
  
    output_audio_file = os.path.join(temp_dir, f"{yt.video_id}.wav")
    
    # Extract audio from the video and save it as a file
    try:
        video = VideoFileClip(video_file)
        video.audio.write_audiofile(output_audio_file)
        video.close() 
    except Exception as e:
        return f"Error extracting audio: {e}"

    return output_audio_file

# Function to convert speech in an audio file to text
def speech_to_text(audio_path, languages=['tr-TR', 'en-US']):
    recognizer = sr.Recognizer() 
    audio_chunks = []
    chunk_duration = 30  # Duration for each audio chunk in seconds

    # Split the audio into chunks of 30 seconds.
    try:
        with sr.AudioFile(audio_path) as source:
            while True:
                audio_chunk = recognizer.record(source, duration=chunk_duration)
                if len(audio_chunk.frame_data) < 1:
                    break
                audio_chunks.append(audio_chunk)
    except Exception as e:
        return f"Error reading audio file: {e}"  # Return None if audio file reading fails

    text_with_timestamps = []
    
    # Start transcribing the audio into text. First try Turkish, if it fails then try English.
    def recognize_chunk(chunk_info):
        chunk, start_time = chunk_info
        for language in languages:
            try:
                print(f"Transcribing in {language}...")
                recognized_text = recognizer.recognize_google(chunk, language=language)
                timestamp = f"{start_time // 60}:{start_time % 60:02d} - "
                return f"{timestamp}{recognized_text} ({language})"
            except sr.UnknownValueError:
                print(f"Unintelligible audio ({language}).")
                continue
            except sr.RequestError as e:
                return f"Google Speech Recognition error: {e}"
        return ""
    
    # Use threads to speed up the processing
    with ThreadPoolExecutor(max_workers=8) as executor:
        start_time = 0
        audio_chunks_with_time = [(chunk, start_time + i * chunk_duration) for i, chunk in enumerate(audio_chunks)]
        results = list(executor.map(recognize_chunk, audio_chunks_with_time))

    text_with_timestamps = "\n".join(filter(None, results))
    
    return text_with_timestamps.strip()

# Main function to process the video
def process_video(input_source):
    yt = YouTube(input_source)
    txtFile = os.path.join(temp_dir, f"{yt.video_id}.txt")
    
    # If a transcription of the video already exists, do not process it again
    if os.path.exists(txtFile):
        print("Transcription already exists.")
        with open(txtFile, "r", encoding="utf-8") as file:
            transcription = " ".join(file.readlines())
    else:
        audio_path = download_and_extract_audio_then_return_audio_path(input_source)
        if audio_path is None:  # Check if audio extraction was successful
            print()
            return None
        
        transcription = speech_to_text(audio_path)
        if transcription:
            with open(txtFile, "w", encoding="utf-8") as file:
                file.write(transcription)

            # Remove the video and audio files after processing
            os.remove(os.path.join(temp_dir, f"{yt.video_id}.mp4"))  # Remove video file
            os.remove(audio_path)  # Remove audio file

    return transcription

