import random
from tkinter import Tk
from Orion_client.view.ui_template import MiniGameWindow


class Minigame1: #remember the number
    def __init__(self):
        self.numbers = "0123456789"
        self.minigame = MiniGameWindow(root, "bob")
        self.game = self.minigame.get_minigame()
        self.minigame.set_header("Number Memory")
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


class Minigame2: #simon says
    def __init__(self):
        self.minigame = MiniGameWindow(root, "bob")
        self.minigame.set_header("Simon Says")
        self.game = self.minigame.get_minigame()
        self.colors = ["red", "green", "blue", "yellow"]
        self.sequence = []
        self.player_sequence = []
        self.turn = 0
        self.tile_size = 150
        self.game.generate_buttons(self.tile_clicked)
        self.tiles = self.game.get_tiles()

    def start_game(self):
        # Generate a new sequence of tiles
        self.sequence = []
        for i in range(5):
            self.sequence.append(random.choice(self.colors))

        # Show the sequence to the player
        self.show_sequence()

    def show_sequence(self):
        # Disable the tiles while showing the sequence
        for tile in self.tiles:
            tile.config(state="disabled")

        # Show each tile in the sequence in order
        for color in self.sequence:
            tile = self.tiles[self.colors.index(color)]
            tile.config(bg=color)
            #TODO WAIT
            tile.config(bg="gray")
            #TODO WAIT

        # Enable the tiles for the player to click
        for tile in self.tiles:
            tile.config(state="normal")

    def tile_clicked(self, event):
        # Get the tile that was clicked
        tile = event.widget

        # Add the color to the player's sequence
        color = self.colors[self.tiles.index(tile)]
        self.player_sequence.append(color)

        # Light up the tile briefly
        tile.config(bg=color)
        #TODO WAIT
        tile.config(bg="gray")

        # Check if the player's sequence matches the computer's sequence
        if self.player_sequence == self.sequence:
            self.turn += 1
            self.player_sequence = []
            if self.turn == 5:
                self.game_over()
            else:
                self.show_sequence()
        elif self.sequence[:len(self.player_sequence)] != self.player_sequence:
            self.game_over()

    def game_over(self):
        # Disable the tiles
        for tile in self.tiles:
            tile.config(state="disabled")

        # Show the game over message

    def get_gameWindow(self):
        return self.minigame


class Minigame3: #Target Shooter
    def __init__(self, master):
        self.minigame = MiniGameWindow(root, "bob")
        self.game = self.minigame.get_minigame()
        self.canvas = self.game.getCanvas()
        self.width = 500
        self.height = 500
        self.score = 0
        self.timer = 10
        self.target_radius = 20
        self.target_color = "#FF0000"
        self.target = None
        self.create_target()
        self.game.bindCanvas(self.shoot)
        self.tick()

    def create_target(self):
        x = random.randint(self.target_radius, self.width - self.target_radius)
        y = random.randint(self.target_radius, self.height - self.target_radius)
        if self.target:
            self.canvas.delete(self.target)
        self.target = self.canvas.create_oval(x - self.target_radius, y - self.target_radius,
                                              x + self.target_radius, y + self.target_radius,
                                              fill=self.target_color)

    def shoot(self, event):
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x, y, x, y)
        if self.target in items:
            self.score += 1
            self.game.set_score(self.score)
            self.create_target()

    def tick(self):
        self.timer -= 1
        self.game.set_timer(f"Time left: {self.timer}")
        if self.timer == 0:
            self.canvas.unbind("<Button-1>")
            self.game.set_timer("Time's up!")
        else:
            print("tick")
            #tick


if __name__ == '__main__':
    root = Tk()
    root.geometry("800x600")

    minigamewindow = Minigame2()

    minigame = minigamewindow.get_gameWindow()
    minigame.pack()
    #minigamewindow.start_game(6)
    minigamewindow.start_game()
    root.mainloop()
