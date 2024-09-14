# TODO 
# Finish the preview page 
# Connect to transcribe and summarize
# Figure out how to display the results in the best way (maybe should be copiable text at least for the summarization) 
# -maybe a separate output page?
# Add a button to record from microphone
# Add toggles to write .txt files by default
# Add buttons to write into txt files (user selectable folder)
# Make the window sizes coherent and make the whole thing prettier
# Stress test for at least a 1,5 hour lecture
#
# IDEAS
# Add different tasks than summarize
# Advanced settings: select models, modify system prompt, audio settings
# Create a product from this - free tier and premium tier

import customtkinter as tk
from system_audio_recorder import get_audio_devices
from CTkListbox import *
from CTkMessagebox import CTkMessagebox
from tkinter import StringVar
from datetime import datetime, timedelta
import os
import wave
import pyaudio
import threading
from pygame import mixer, event
from mutagen.mp3 import MP3
import platform

audio_device_keys = []
audio_device_names = []
audio_device_dict = {}
p = None
audio_devices = None
audio_file = None # Audio file to use for nlp
now_recording = False
is_paused = False
audio_loaded = False
new_load = True
audio_length = 0
timeline_position = 0
after_id_label = None
after_id_timeline = None
absolute_position = 0
operating_system = None
MUSIC_DONE = event.custom_type() 

def open_file():
    global audio_file
    global audio_loaded
    global is_paused

    if audio_loaded:
        if not is_paused:
            pause_audio()

    file_path = tk.filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav"), ("Audio Files", "*.mp3")])
    audio_file = file_path
    if audio_file is not None:
        # Clean the UI
        label.pack_forget()
        load_audio()
        preview_page()
    else:
        CTkMessagebox(title="Error", message="Could not find audio file at given location")

def get_os():
    global operating_system
    system = platform.system()
    if system == 'Darwin':
        operating_system = "MacOS"
    else:
        operating_system = system

def record_system_audio(filename, p, input_device, input_device_index):
    global audio_file
    global now_recording
    folder = "./Audio"
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = folder + "/" + filename

    # Variables
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = input_device['sample_rates'][0] # Choose one of the available rates

    frames = []  # Initialize array to store frames

    try:
        print('Recording')
        stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True,
                    input_device_index=input_device_index)

        start_time = datetime.now()
        while now_recording:
            data = stream.read(chunk)
            frames.append(data)
            elapsed_time = datetime.now() - start_time
            elapsed_time_str = str(elapsed_time).split(".")[0]
            elapsed_time_label.configure(text=f"{elapsed_time_str}")
            window.update()

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

    except KeyboardInterrupt:
        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"Audio file saved to {filename}")
    audio_file = filename
    return filename

def seek_forward(seconds=10):
    global audio_length
    global absolute_position
    current_pos = mixer.music.get_pos() / 1000
    absolute_position += seconds
    new_pos = current_pos + absolute_position
    print(new_pos)
    mixer.music.set_pos(new_pos)
    #update_time_labels()
    #update_timeline_position(new_pos/audio_length.seconds)

def seek_backward(seconds=10):
    global audio_length
    global absolute_position
    current_pos = mixer.music.get_pos() / 1000
    absolute_position -= seconds
    new_pos = current_pos + absolute_position
    if new_pos < 0:
        new_pos = 0
        absolute_position = 0
        mixer.music.play()
    print(new_pos)
    mixer.music.set_pos(new_pos)
    #update_time_labels()
    #update_timeline_position(new_pos/audio_length.seconds)

# Update the format of the labels with the actual elapsed and remaining time
def update_time_labels(position=None):
    global audio_file
    global audio_loaded
    global audio_length
    global new_load
    global absolute_position

    # Update the format of the labels
    if position is not None:
        elapsed_time = str(timedelta(seconds=position))
        elapsed_time = elapsed_time[:-5] # Remove the last 3 digits for milliseconds
        elapsed_playback_time_label.configure(text=elapsed_time)

    if audio_file:
        if audio_loaded:
            mixer_pos = mixer.music.get_pos()
            if new_load or mixer_pos < 0:
                elapsed_time = str(timedelta(milliseconds=1))
            else:
                abs_pos = mixer_pos + 1000 * absolute_position
                elapsed_time = str(timedelta(milliseconds=int(abs_pos)))
            elapsed_time = elapsed_time[:-5] # Remove the last 3 digits for milliseconds
            elapsed_playback_time_label.configure(text=elapsed_time)
        remaining_time_str = str(audio_length).split(".")[0]
        remaining_time_label.configure(text=f" / {remaining_time_str}")

    if not mixer.music.get_busy() and not is_paused:
        mixer.music.stop()
        new_load = True
        absolute_position = 0
    window.after(100, update_time_labels)

# Function to update the timeline position based on the current playback time
def update_timeline_position(position=None):
    global audio_file
    global audio_loaded
    global timeline_position
    global audio_length
    global new_load

    if position is None:
        if audio_file and audio_loaded:
            if new_load:
                current_position = 0.0000000001
            else:
                current_position = absolute_position + mixer.music.get_pos() / 1000  # Convert milliseconds to seconds
            timeline_position = (current_position / audio_length.seconds)
            timeline_bar.set(timeline_position)
    else:
        timeline_position = position
        timeline_bar.set(timeline_position)
    window.after(100, update_timeline_position)

def get_audio_length(audio_file):
    if audio_file.endswith(".wav"):
        with wave.open(audio_file, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            return timedelta(seconds=int(duration))
    elif audio_file.endswith(".mp3"):
        audio = MP3(audio_file)
        duration = audio.info.length
        return timedelta(seconds=int(duration))
    else:
        return None

def load_audio():
    global audio_loaded
    global audio_file
    global audio_length
    global new_load
    global absolute_position
    mixer.init()
    if audio_file is not None:
        mixer.music.load(audio_file)
        audio_loaded = True
        audio_length = get_audio_length(audio_file)
        new_load = True
        absolute_position = 0
        if operating_system == "MacOS":
            audio_file_label.configure(text=audio_file.split("/")[-1])
        else:
            audio_file_label.configure(text=audio_file)

def play_audio():
    global audio_file
    global is_paused
    global audio_loaded
    global new_load

    if not audio_loaded:
        if audio_file is not None:
            load_audio()
            # Set the playhead position to the current position
            mixer.music.play()
            is_paused = False
        else:
            CTkMessagebox(title="Error", message="No audio file available")
    elif new_load:
        mixer.music.play()
        pause_button.configure(text="Pause") 
        is_paused = False
        new_load = False
    else: 
        mixer.music.unpause()
        pause_button.configure(text="Pause") 
        is_paused = False
    mixer.music.set_endevent(MUSIC_DONE)

def pause_audio():
    global audio_file
    global is_paused
    global audio_loaded
    global new_load
    if audio_file is not None:
        if not is_paused:
            # Pause the playback of the audio file using the mixer from pygame library
            mixer.music.pause()
            is_paused = True
            pause_button.configure(text="Stop") 
        else:
            mixer.music.stop()
            new_load = True
            pause_button.configure(text="Pause") 
            elapsed_playback_time_label.configure(text="0:00:00.0")
            timeline_bar.set(0)
    else:
        CTkMessagebox(title="Error", message="No audio file available")

def start_recording():
    global audio_file
    global audio_device_dict
    global now_recording
    # Clear global variable 
    audio_file = None

    selected_device = device_listbox.get(device_listbox.curselection())
    if selected_device is None:
        CTkMessagebox(title="Error", message="You need to have an audio device selected")

    else:
        # Clean the UI
        label.pack_forget()
        record_button.pack_forget()
        choose_file_button.pack_forget()
        start_recording_button.pack_forget()
        back_button.pack_forget()
        device_listbox.pack_forget()

        # Create a temporary page
        rec_label.pack()
        elapsed_time_label.pack()
        stop_button.pack()

        # Start recording
        start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        device_id = audio_device_dict[selected_device]
        input_device = audio_devices[device_id]
        filename = fr"ui_recording_{start_time}.wav"
        now_recording = True
        def thread_callback():
            audio_file = record_system_audio(filename, p, input_device, device_id)
        
        threading.Thread(target=thread_callback).start()

def recording_options_page():
    global audio_device_dict
    global audio_device_keys
    global audio_device_names
    global p
    global audio_devices

    # Clear variables
    if p is not None:
        p.terminate()
        p = None
    audio_devices = None
    # Get the available audio devices
    p, audio_devices = get_audio_devices()
    
    # Create a list of audio device keys and names
    audio_device_keys = list(audio_devices.keys())
    audio_device_names = [audio_devices[key]["name"] for key in audio_device_keys]
    # Create a dictionary with name as key and key as value
    audio_device_dict = {name: key for name, key in zip(audio_device_names, audio_device_keys)}

    for i, device_name in enumerate(audio_device_names):
        # Add each device name as an item in the listbox
        device_listbox.insert(tk.END, device_name)
        # Set the id as the item's data
        #device_listbox.set_item_data(i, audio_device_keys[i])

    # Pack items
    choose_device_label.pack()
    device_listbox.pack()
    start_recording_button.pack()
    back_button.pack()

    # Clean the UI
    label.pack_forget()
    record_button.pack_forget()
    choose_file_button.pack_forget()


def front_page():
    # Place the record_button and choose_file_button
    label.pack()
    record_button.pack()
    choose_file_button.pack()

    # Clean the UI
    label.pack_forget()
    start_recording_button.pack_forget()
    back_button.pack_forget()
    device_listbox.pack_forget()

def stop_recording():
    global now_recording
    now_recording = False

    # Clear the UI
    rec_label.pack_forget()
    stop_button.pack_forget()
    elapsed_time_label.pack_forget()
    choose_device_label.pack_forget()
    preview_page()

def preview_page():
    global audio_file
    global audio_length
    # Create a preview page
    record_button.pack()
    choose_file_button.pack()
    preview_label.pack()
    audio_file_label.pack()

    elapsed_playback_time_label.pack(side=tk.LEFT)
    remaining_time_label.pack(side=tk.LEFT)

    pause_button.pack(side=tk.BOTTOM)
    play_button.pack(side=tk.BOTTOM)
    process_page_button.pack(side=tk.RIGHT)
    seek_backward_button.pack(side=tk.LEFT)
    seek_forward_button.pack(side=tk.LEFT)

    timeline_bar.pack()
    timeline_bar.set(0)

    while True:
        if audio_file is None:
            continue
        else:
            load_audio()
            break
    update_time_labels()
    update_timeline_position()

def processing_page():
    # Clear music
    mixer.music.stop()
    mixer.music.unload()

    # Clear previous page except filename
    record_button.pack_forget()
    choose_file_button.pack_forget()
    preview_label.pack_forget()
    elapsed_playback_time_label.pack_forget()
    remaining_time_label.pack_forget()
    pause_button.pack_forget()
    play_button.pack_forget()
    process_page_button.pack_forget()
    timeline_bar.pack_forget()
    seek_backward_button.pack_forget()
    seek_forward_button.pack_forget()
    audio_file_label.pack_forget()

    # Pack page contents
    audio_file_label.pack()
    gpt_task_label.pack()
    gpt_task_dropdown.pack()
    whisper_model_size_label.pack()
    whisper_model_size_dropdown.pack()
    output_processed_switch.pack()
    output_transcription_switch.pack()
    cancel_processing_button.pack()
    process_button.pack()
    

def process_audio():
    # TODO
    # Get parameters for transcription and gpt task
    # run them and display progress 
    # Display results when done
    print("You clicked me :D")

def cancel_processing():
    audio_file_label.pack_forget()
    gpt_task_label.pack_forget()
    gpt_task_dropdown.pack_forget()
    whisper_model_size_label.pack_forget()
    whisper_model_size_dropdown.pack_forget()
    output_processed_switch.pack_forget()
    output_transcription_switch.pack_forget()
    cancel_processing_button.pack_forget()
    process_button.pack_forget()
    preview_page()

# Create the main window
window = tk.CTk()
window.title("Meeting Copilot")
window.geometry("600x400")
tk.set_appearance_mode("System")
tk.set_default_color_theme("themes/lavender.json") 

get_os()

# Recording options page
choose_device_label = tk.CTkLabel(window, text="Choose input audio device")
back_button = tk.CTkButton(window, text="Back", command=front_page)
start_recording_button = tk.CTkButton(window, text="Start Recording", command=start_recording)
device_listbox = CTkListbox(window)

# Recording page
rec_label = tk.CTkLabel(window, text="Recording in progress...")
elapsed_time_label = tk.CTkLabel(window, text="00:00:00")
stop_button = tk.CTkButton(window, text="Stop Recording", command=stop_recording)

# Preview page
preview_label = tk.CTkLabel(window, text="Preview")
play_button = tk.CTkButton(window, text="Play", command=play_audio)
pause_button = tk.CTkButton(window, text="Pause", command=pause_audio)
elapsed_playback_time_label = tk.CTkLabel(window, text="0:00:00.0")
remaining_time_label = tk.CTkLabel(window, text=" / 0:00:00")
timeline_bar = tk.CTkProgressBar(window)
process_page_button = tk.CTkButton(window, text="Process audio", command=processing_page)
seek_forward_button = tk.CTkButton(window, text=">> 10s", command=seek_forward)
seek_backward_button = tk.CTkButton(window, text="<< 10s", command=seek_backward)
audio_file_label = tk.CTkLabel(window, text="")

# Main page
label = tk.CTkLabel(window, text="Transcribe and summarize!")
label.pack()
record_button = tk.CTkButton(window, text="Record System Audio", command=recording_options_page)
record_button.pack()
choose_file_button = tk.CTkButton(window, text="Choose Existing Audio File", command=open_file)
choose_file_button.pack()

# Processing page
cancel_processing_button = tk.CTkButton(window, text="Cancel", command=cancel_processing)
process_button = tk.CTkButton(window, text="Process", command=process_audio)
output_processed_switch = tk.CTkSwitch(window, text="Output processed text as txt-file")
output_transcription_switch = tk.CTkSwitch(window, text="Output complete transcription as txt-file")

whisper_model_size_label = tk.CTkLabel(window, text="Transcription speed")
whisper_model_size_options = ["Fastest, lowest accuracy ", "Fast, good accuracy (recommended)", "Slow, very good accuracy", "Slowest, highest accuracy"]
whisper_model_size_dropdown = tk.CTkOptionMenu(window, values=whisper_model_size_options)
whisper_model_size_dropdown.set("Fast, good accuracy (recommended)")

gpt_task_label = tk.CTkLabel(window, text="Copilot task")
gpt_task_options = ["Summarization"]
gpt_task_dropdown = tk.CTkOptionMenu(window, values=gpt_task_options)

# Start the main event loop
window.mainloop()
