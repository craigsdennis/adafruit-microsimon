"""
MicroSimon for the adafruit Circuit Playground Express.

"""
import array
import math
import random
import time

import audioio
import board
from digitalio import DigitalInOut, Direction
import neopixel
import touchio


SAMPLERATE = 8000
START_COUNT = 4

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=.2)
spkrenable = DigitalInOut(board.SPEAKER_ENABLE)
spkrenable.direction = Direction.OUTPUT
spkrenable.value = True

# Yoinked this from another example
def create_sample(frequency):
    length = SAMPLERATE // frequency
    sine_wave = array.array("H", [0] * int(length))
    for i in range(length):
        sine_wave[i] = int(math.sin(math.pi * 2 * i / 18) * (2 ** 15) + 2 ** 15)
    sample = audioio.AudioOut(board.SPEAKER, sine_wave)
    # Mismatch is intentional...weird API?
    sample.frequency = SAMPLERATE
    return sample

def clear():
    pixels.fill((0, 0, 0))
    pixels.show()


class SimonButton:

    def __init__(self, color, pixels, frequency, buttons):
        self.color = color
        self.pixels = pixels
        self.touch_buttons = [touchio.TouchIn(btn) for btn in buttons]
        self.sample = create_sample(frequency)

    def activate(self, seconds=1):
        clear()
        self.show()
        self.play_sound(seconds)

    def show(self):
        for pixel_index in self.pixels:
            pixels[pixel_index] = self.color

    def play_sound(self, seconds):
        self.sample.play(loop=True)
        time.sleep(seconds)
        self.sample.stop()

    def is_pressed(self):
        return any(tb.value for tb in self.touch_buttons)

# Green, Yellow, Blue, Red buttons
all_simon_buttons = [
    SimonButton((0, 255, 0), (0, 1), 261.63, (board.A4, board.A5)),
    SimonButton((255, 255, 0), (3, 4), 293.66, (board.A6, board.A7)),
    SimonButton((0, 0, 255), (8, 9), 329.63, (board.A2, board.A3)),
    SimonButton((255, 0, 0), (5, 6), 349.23, (board.A1,)),
]

# Finds the chosen button
def get_simon_button():
    while True:
        for simon_button in all_simon_buttons:
            if simon_button.is_pressed():
                return simon_button
        time.sleep(0.1)

# Global list of expected buttons
master = []

def add_random_button():
    master.append(random.choice(all_simon_buttons))


for _ in range(0, START_COUNT):
    add_random_button()

def display_master():
    for simon_button in master:
        # Increase speed as master grows
        simon_button.activate(START_COUNT / len(master))

def play_failure():
    pixels.fill((255, 0, 0))
    sample = create_sample(16.35)
    sample.play(loop=True)
    time.sleep(2)
    sample.stop()
    clear()

game_over = False
while not game_over:
    display_master()
    clear()
    for expected in master:
        actual = get_simon_button()
        game_over = expected != actual
        if game_over:
            break
        actual.activate()
    if not game_over:
        add_random_button()

play_failure()
