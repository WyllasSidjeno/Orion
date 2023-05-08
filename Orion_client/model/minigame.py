import math
import random
from tkinter import Tk
from Orion_client.view.ui_template import MiniGameWindow

class Minigame1:
    def __init__(self):
        self.numbers = "0123456789"
        self.minigame = MiniGameWindow(root, "bob")
        self.game = self.minigame.get_minigame()
        self.sequence = ""
        self.guess = ""
        self.time = 0
        self.game.bind_button(self.check_guess)

    def generate_sequence(self, length):
        return [random.choice(self.numbers) for _ in range(length)]

    def get_guess(self):
        self.guess = self.game.get_Textbox()

    def check_guess(self):
        self.get_guess()

        if self.guess == self.sequence:
            print("true")
            self.game.winState()
        else:
            print("false")
            self.game.failState()

    def tick(self):
        self.time += 1
        print(self.time)

    def play_game(self, length):
        sequence = self.generate_sequence(length)
        self.sequence = "".join(sequence)
        self.game.setTextbox(self.sequence)
        self.game.disableInput()


        if self.time <= 25:
            self.tick()
        else:
            self.game.setTextbox(" ")
            self.game.enableInput()


    def get_gameWindow(self):
        return self.minigame


if __name__ == '__main__':
    root = Tk()
    root.geometry("800x600")

    minigamewindow = Minigame1()

    minigame = minigamewindow.get_gameWindow()
    minigame.pack()
    minigamewindow.play_game(6)

    root.mainloop()