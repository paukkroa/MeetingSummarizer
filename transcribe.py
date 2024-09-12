import whisper
from whisper.utils import get_writer
import os

def transcribe(filepath, model_size="small", language=None, verbose=False, write_output=False, output_directory="./Transcriptions", filename='transcription'):
    model = whisper.load_model(model_size)
    if not language:
        result = model.transcribe(filepath, fp16=False, verbose=verbose)
    else:
        result = model.transcribe(filepath, language=language, fp16=False, verbose=verbose)
    
    transcribed_text = result["text"]

    # Write results
    if write_output:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        output_file = output_directory + "/" + filename + ".txt"
        with open(output_file, "w", encoding="utf-8") as txt:
            txt.write(transcribed_text)
        print(f"Transcription saved to {output_file}")

    return transcribed_text

