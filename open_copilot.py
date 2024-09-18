from system_audio_recorder import record_system_audio
from transcribe import transcribe
from openai_handler import handle_gpt
import os
from datetime import datetime
from time import strftime
from whisper.tokenizer import LANGUAGES
import warnings

PATH_TO_EXISTING_AUDIO_FILE = None
VERBOSE = False
WHISPER_MODEL_SIZE = "small"
GPT_MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = None

warnings.simplefilter(action='ignore', category=FutureWarning)

def main(output_transcription=True, output_summarization=True):
    flag = False
    # Check if given file is valid
    if not (PATH_TO_EXISTING_AUDIO_FILE is None):
        if os.path.isfile(PATH_TO_EXISTING_AUDIO_FILE):
            print(f"Found an existing audio file: {PATH_TO_EXISTING_AUDIO_FILE}")
            flag = input("Do you want to use this file? (y/n): ")
            if flag.lower() == "y":
                flag = True
            else:
                flag = False
        else:
            print(f"Warning: Could not find a file in given location {PATH_TO_EXISTING_AUDIO_FILE}")
    
    start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Record system audio
    if not flag:
        filename = fr"system_recording_{start_time}.wav"
        audio_file = record_system_audio(filename)
    
    # Use existing audio file if it was valid
    else:
        audio_file = PATH_TO_EXISTING_AUDIO_FILE

    print(f"Input audio file: {audio_file}")

    # Transcribe text
    language = input("Enter language if known (for better performance) e.g. 'fi': ")
    if language in LANGUAGES.keys():
        transcibed_text = transcribe(audio_file, 
                                     model_size=WHISPER_MODEL_SIZE, 
                                     language=language, 
                                     verbose=VERBOSE, 
                                     write_output=output_transcription,
                                     filename=f"transcription_{start_time}")
    else: 
        print("Using any language")
        transcibed_text = transcribe(audio_file, 
                                     model_size=WHISPER_MODEL_SIZE, 
                                     verbose=VERBOSE, 
                                     write_output=output_transcription,
                                     filename=f"transcription_{start_time}")

    # Summarize text
    summarized_text = handle_gpt(transcibed_text, 
                                     model=GPT_MODEL, 
                                     write_output=output_summarization,
                                     filename=f"summarization_{start_time}",
                                     system_prompt=SYSTEM_PROMPT)
    
    print("Here is your summarization:")
    print(summarized_text)

if __name__ == "__main__":
    main()