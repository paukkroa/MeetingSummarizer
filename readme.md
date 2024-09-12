# Lecture Summarizer

A tool to capture system audio and create transcriptions and summarizations from it.
Uses OpenAI's Whisper for transcription and OpenAI API for summarization.

Version: 0.1

## Table of Contents

- [Operating Systems](#operatingsystems)
- [Installation](#installation)
- [Usage](#usage)

## Operating Systems

System audio recording currently only supported for MacOS. 

## Installation

Install requirements from requirements.txt. Import any missing packages.

If you want to record system audio:

MacOS:
Install BlackHole (2 channel) from Existential audio: https://existential.audio/blackhole/
This is used to route system audio to Python.

If you are using BlackHole as the output device then you won't hear any audio.
To make system audio hearable, you need to create a Multi-Output Device in Audio MIDI Settings. 
Select your primary output (e.g. Macbook Speakers) as primary output and BlackHole as secondary output.
Choose this Multi-Output Device as your output in the Sound menu.

Windows:
Coming soon

## Usage

Make sure to paste your OpenAI API key and ORG_ID to envero.py or use some other method of authentication.

You can use an existing audiofile (wav or mp3) or record system audio from a live lecture/meeting for example.

Set the path to the existing audio file in global variables under lecture_summarizer.py

Launch the code in your terminal with 

```
python3 lecture_summarizer.py
```

The program will prompt you to use the existing audio_file if found

If you choose to record system audio, the program will prompt you to select the device.

In MacOS:

Select Blackhole 2ch by giving the id of it.
E.g. 
```
Input Device id  0  -  BlackHole 2ch
Input Device id  1  -  MacBook Pro Microphone
```

--> write '1'

Then press any key to start recording when you are ready

To stop the recording, hit CTRL-C. The recording will be saved under the Audio/ folder.

After recording has finished or if you are using an existing file, the program will prompt you to give the language of the file if it is known. Otherwise autodetection will be used.

Then, transcription and summarization are ran and results will be saved under Transcriptions/ and Summarizations/ folders respectively.

That's it, enjoy! 😊
