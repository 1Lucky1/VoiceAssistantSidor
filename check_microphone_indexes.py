import pyaudio

def list_microphones():
    p = pyaudio.PyAudio()
    mic_count = p.get_device_count()

    print("Доступные микрофоны:")
    for i in range(mic_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:  # Проверяем, что устройство поддерживает ввод
            print(f"Индекс: {i}, Название: {device_info['name']}")

    p.terminate()

if __name__ == "__main__":
    list_microphones()