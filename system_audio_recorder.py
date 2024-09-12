import platform
import pyaudio
import wave
import os

def get_audio_devices():
    # Get the system we are working with
    system = platform.system()
    if system == 'Darwin': # MacOS
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        available_devices = {}
        sample_rates = [44100, 48000, 88200, 96000]

        print("Found these audio devices:")
        for i in range(0, numdevices):
            devinfo = p.get_device_info_by_host_api_device_index(0, i)

            if (devinfo.get('maxInputChannels')) > 0: # check that there are inputs
                device_rates = []
                for sample_rate in sample_rates:
                    # Check if the sample rates match to supported ones
                    if p.is_format_supported(sample_rate, 
                                input_device=devinfo['index'],
                                input_channels=devinfo['maxInputChannels'],
                                input_format=pyaudio.paInt16):
                        device_rates.append(sample_rate)

                available_devices[i] = {"name": devinfo.get('name'),
                                        "sample_rates": device_rates}
                print("Input Device id ", i, " - ", devinfo.get('name'))
    else:
        raise Exception("Unsupported system :(")
    
    return p, available_devices

def choose_input_device(available_devices):
    input_device_index = int(input("Choose your input device id: "))
    input_device = available_devices[input_device_index]
    print(f"You chose: {input_device['name']}")
    print(f"Sample rates: {input_device['sample_rates']}")
    return input_device, input_device_index

def record_system_audio(filename="output.wav"):
    folder = "./Audio"
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = folder + "/" + filename
    p, available_devices = get_audio_devices()
    input_device, input_device_index = choose_input_device(available_devices)

    # Variables
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = input_device['sample_rates'][0] # Choose one of the available rates

    frames = []  # Initialize array to store frames

    input("Press any key to start recording, CTRL-C to stop")
    try:
        print('Recording')
        stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True,
                    input_device_index=input_device_index)
        while True:
            data = stream.read(chunk)
            frames.append(data)
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
    return filename

def main():
    record_system_audio()

if __name__ == "__main__":
    main()