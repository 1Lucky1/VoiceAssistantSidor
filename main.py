import logging
import ospip
import subprocess
import threading
import time
import webbrowser
from random import choice

import pyaudio
import pygame
import vosk

# Настройка логирования
logging.basicConfig(filename='voice_assistant.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

audio_directory = r'.\audio'
telegram_audio = []
vk_audio = []

vk_phrases = ["века", "быка", "ка", "вака", "блэка"]
telega_phrases = ["телегу"]
check_state_phrases = ["ты тут", "приём", "отзовись"]

pygame.init()
pygame.mixer.init()


class VoiceAssistant:
    def __init__(self):
        self.model = vosk.Model("./vosk-model-small-ru-0.22")
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)

        self.p = pyaudio.PyAudio()
        self.stream = None

        self.microphone_index = 0  # Индекс микрофона для использования
        self.current_microphone = None

        self.is_listening = False

    def set_microphone(self, index):
        self.microphone_index = index
        self.current_microphone = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True,
                                              frames_per_buffer=8192, input_device_index=self.microphone_index)

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            logging.info("Говорите...")
            play_audio(os.path.join(audio_directory, "start_enhanced.mp3"))

    def stop_listening(self):
        if self.is_listening:
            self.is_listening = False
            logging.info("Остановлено.")

    def listen(self):
        if self.current_microphone is None:
            logging.error("Микрофон не установлен.")
            return

        while True:
            if self.is_listening:
                data = self.current_microphone.read(4096)
                if self.recognizer.AcceptWaveform(data):
                    text = self.recognizer.FinalResult().split('"')[3]
                    if text == "сидорович":
                        pass
                    elif "сидорович" in text:
                        check_for_new_audio_files()
                        logging.info(f"Распознано: {text}")
                        self.process_result(text)

            time.sleep(0.01)

    @staticmethod
    def process_result(result):
        if "сидорович открой" in result:
            result = result.split("сидорович открой")[1].replace(" ", "")
            if result in telega_phrases:
                play_audio(choice(telegram_audio))
                subprocess.run(r'.\shortcuts\Telegram.lnk', shell=True)
            elif result in vk_phrases:
                play_audio(choice(vk_audio))
                webbrowser.open("https://vk.com")
        elif result.split(" ", 1)[1] in check_state_phrases:
            play_audio(os.path.join(audio_directory, "iamhere.mp3"))


def check_for_new_audio_files():
    global telegram_audio
    global vk_audio
    for filename in os.listdir(audio_directory):
        if 'telega' in filename:
            telegram_audio.append(os.path.join(audio_directory, filename))
        elif 'vk' in filename:
            vk_audio.append(os.path.join(audio_directory, filename))


def play_audio(audio, is_for_thread=True):
    if is_for_thread:
        threading.Thread(target=play_audio, args=(audio, False)).start()
    else:
        sound = pygame.mixer.Sound(audio)
        sound.play()
        while pygame.mixer.get_busy():
            time.sleep(0.1)


def main():
    assistant = VoiceAssistant()

    # Устанавливаем микрофон
    assistant.set_microphone(2)  # Использую студийник

    # Запускаем прослушивание в основном потоке
    logging.info("Запуск распознавания...")

    try:
        while True:
            assistant.start_listening()
            assistant.listen()  # Слушаем в текущем потоке
    except KeyboardInterrupt:
        pass

    logging.info("Завершение работы.")


if __name__ == "__main__":
    main()
