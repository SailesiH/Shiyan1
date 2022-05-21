import tkinter as tk
import random
from threading import Lock

COLORS = ['gray', 'lightgreen', 'pink', 'blue', 'orange', 'purple', 'red', 'yellow', 'cyan']


class Columns():
    GAME_HEIGHT = 20
    GAME_WIDTH = 10
    #initial scores
    SCORE_PER_ELIMINATED_LINES = (0, 40, 100, 300, 1200)
    TETROMINOS = [
        [(0, 0), (0, 1), (1, 0), (1, 1)],  # O
        [(0, 0), (0, 1), (1, 1), (2, 1)],  # L
        [(0, 1), (1, 1), (2, 1), (2, 0)],  # J
        [(0, 1), (1, 0), (1, 1), (2, 0)],  # Z
        [(0, 1), (1, 0), (1, 1), (2, 1)],  # T
        [(0, 0), (1, 0), (1, 1), (2, 1)],  # S
        [(0, 1), (1, 1), (2, 1), (3, 1)],  # I
    ]

    def __init__(self):
        self.field = [[0 for c in range(Columns.GAME_WIDTH)] for r in range(Columns.GAME_HEIGHT)]
        self.score = 0
        # for the levels
        self.level = 0
        self.total_lines_eliminated = 0
        # for the levels


        self.move_lock = Lock()
        self.reset_columns()

        self.game_over = False

    def reset_columns(self):
        self.tetromino = random.choice(Columns.TETROMINOS)[:]
        self.tetromino_color = random.randint(1, len(COLORS) - 1)
        #self.tetromino_offset = [-2, Columns.GAME_WIDTH // 2]
        self.tetromino_offset = [-2, Columns.GAME_WIDTH // 2]

        self.game_over = any(not self.is_cell_free(r, c) for (r, c) in self.get_columns_coords())

    def get_columns_coords(self):
        return [(r + self.tetromino_offset[0], c + self.tetromino_offset[1]) for (r, c) in self.tetromino]

    def apply_columns(self):
        for (r, c) in self.get_columns_coords():
            self.field[r][c] = self.tetromino_color

        #destroying the row fully constructed.
        new_field = [row for row in self.field if any(tile == 0 for tile in row)]
        lines_eliminated = len(self.field) - len(new_field)
        self.total_lines_eliminated += lines_eliminated
        self.field = [[0] * Columns.GAME_WIDTH for x in range(lines_eliminated)] + new_field
        self.reset_columns()
        #destroying the row fully constructed.

        #a loop to get a score (line/s eliminated * level+1)
        self.score += Columns.SCORE_PER_ELIMINATED_LINES[lines_eliminated] * (self.level + 1)

        #if you clear 10 rows adds to a level, the higher the level, the clock increases
        self.level = self.total_lines_eliminated // 10

    #random pick from index one, since index zero is for the rectangles
    def get_color(self, r, c):
        return self.tetromino_color if (r, c) in self.get_columns_coords() else self.field[r][c]

    #to ensure the shapes don't go off the rectangles.
    def is_cell_free(self, r, c):
        return r < Columns.GAME_HEIGHT and 0 <= c < Columns.GAME_WIDTH and (r < 0 or self.field[r][c] == 0)
    #(and (r < 0 or self.field[r][c] == 0) - ensures the shapes on top of the other without overriding.

    def move(self, dr, dc):
        with self.move_lock:
            if self.game_over:
                return

            if all(self.is_cell_free(r + dr, c + dc) for (r, c) in self.get_columns_coords()):
                self.tetromino_offset = [self.tetromino_offset[0] + dr, self.tetromino_offset[1] + dc]
                #to determine whether there any lines above
            elif dr == 1 and dc == 0:
                self.game_over = any(r < 0 for (r, c) in self.get_columns_coords())
                if not self.game_over:
                    self.apply_columns()

    def rotate(self):
        with self.move_lock:
            if self.game_over:
                self.__init__()
                return

            ys = [r for (r, c) in self.tetromino]
            xs = [c for (r, c) in self.tetromino]
            size = max(max(ys) - min(ys), max(xs) - min(xs))
            rotated_tetromino = [(c, size - r) for (r, c) in self.tetromino]
            wallkick_offset = self.tetromino_offset[:]
            tetromino_coord = [(r + wallkick_offset[0], c + wallkick_offset[1]) for (r, c) in rotated_tetromino]
            min_x = min(c for r, c in tetromino_coord)
            max_x = max(c for r, c in tetromino_coord)
            max_y = max(r for r, c in tetromino_coord)
            wallkick_offset[1] -= min(0, min_x)
            wallkick_offset[1] += min(0, Columns.GAME_WIDTH - (1 + max_x))
            wallkick_offset[0] += min(0, Columns.GAME_HEIGHT - (1 + max_y))

            tetromino_coord = [(r + wallkick_offset[0], c + wallkick_offset[1]) for (r, c) in rotated_tetromino]
            if all(self.is_cell_free(r, c) for (r, c) in tetromino_coord):
                self.tetromino, self.tetromino_offset = rotated_tetromino, wallkick_offset


#first part ....
#create the form abd panel
class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.Columns = Columns()
        self.pack()
        self.create_widgets()
        self.update_clock()

    #to set the timing for each shape
    def update_clock(self):
        self.Columns.move(1, 0)
        self.update()
        #the next shape appearing after n seconds
        # self.master.after(1000, self.update_clock) - this is the initial without increasing speed with increase to level.

        #this decreases the clock with increase of level.
        self.master.after(int(300 * (0.66 ** self.Columns.level)), self.update_clock)

    def create_widgets(self):
        PIECE_SIZE = 30
        self.canvas = tk.Canvas(self, height=PIECE_SIZE * self.Columns.GAME_HEIGHT,
                                width=PIECE_SIZE * self.Columns.GAME_WIDTH, bg="black", bd=0)

        #to make the rotation of the shapes.
        self.canvas.bind('<Left>', lambda _: (self.Columns.move(0, -1), self.update()))
        self.canvas.bind('<Right>', lambda _: (self.Columns.move(0, 1), self.update()))
        self.canvas.bind('<Down>', lambda _: (self.Columns.move(1, 0), self.update()))
        #to make the rotation of the shapes by the letters l,r and d
        self.canvas.bind('l', lambda _: (self.Columns.move(0, -1), self.update()))
        self.canvas.bind('r', lambda _: (self.Columns.move(0, 1), self.update()))
        self.canvas.bind('d', lambda _: (self.Columns.move(1, 0), self.update()))
        
        #Up calls the rotate function
        self.canvas.bind('<Up>', lambda _: (self.Columns.rotate(), self.update()))
        self.canvas.focus_set()

        #rectangles creating the grid
        self.rectangles = [
            self.canvas.create_rectangle(c * PIECE_SIZE, r * PIECE_SIZE, (c + 1) * PIECE_SIZE, (r + 1) * PIECE_SIZE)
            for r in range(self.Columns.GAME_HEIGHT) for c in range(self.Columns.GAME_WIDTH)
        ]
        self.canvas.pack(side="left")
        #the left panel for the scores and level.
        self.game_title_msg = tk.Label(self, anchor='w', width=11, font=("Trajan", 30), justify='center')
        self.game_title_msg.pack(side="top")
        self.score_status_msg = tk.Label(self, anchor='w', width=11, font=("Courier", 30))
        self.score_status_msg.pack(side="top")
        self.level_status_msg = tk.Label(self, anchor='w', width=11, font=("Courier", 25))
        self.level_status_msg.pack(side="top")
        self.game_over_msg = tk.Label(self, anchor='w', width=11, font=("comics-ans", 24), fg='red')
        self.game_over_msg.pack(side="top")

    def update(self):
        #providing bg color to the rectangles
        for i, _id in enumerate(self.rectangles):
            color_num = self.Columns.get_color(i // self.Columns.GAME_WIDTH, i % self.Columns.GAME_WIDTH)
            self.canvas.itemconfig(_id, fill=COLORS[color_num])

        self.game_title_msg['text'] = "COLUMNS"
        self.score_status_msg['text'] = " Score: {}".format(self.Columns.score)
        self.level_status_msg['text'] = " Level : {}".format(self.Columns.level)
        self.game_over_msg['text'] = "GAME OVER.\nPress UP\nto reset" if self.Columns.game_over else ""
        #pressing UP calls line 90


root = tk.Tk()
root.title("Jia you")
app = Application(master=root)
app.mainloop()
