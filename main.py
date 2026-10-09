import tkinter as tk
from tkinter import messagebox
import random
import time


class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Python-Minesweeper")
        self.root.resizable(False, False)

        # 默认难度（初级）
        self.rows = 9
        self.cols = 9
        self.mines_count = 10

        self.is_first_click = True
        self.is_game_over = False
        self.flags_count = 0
        self.revealed_count = 0

        self.grid_buttons = []
        self.mines = []
        self.numbers = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        self.start_time = 0
        self.timer_running = False

        self.setup_ui()
        self.create_board()

    def setup_ui(self):
        # 顶部状态栏
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        # 剩余雷数
        self.mine_label = tk.Label(top_frame, text=f"💣 {self.mines_count}", font=("Arial", 14, "bold"), width=6)
        self.mine_label.pack(side=tk.LEFT, padx=10)

        # 重置按钮
        self.reset_btn = tk.Button(top_frame, text="🙂", font=("Arial", 16), command=self.reset_game)
        self.reset_btn.pack(side=tk.LEFT, padx=10)

        # 计时器
        self.time_label = tk.Label(top_frame, text="⏱ 000", font=("Arial", 14, "bold"), width=6)
        self.time_label.pack(side=tk.LEFT, padx=10)

        # 难度选择
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=5)
        for difficulty, (r, c, m) in {"Easy": (9, 9, 12), "Middle": (16, 16, 50), "Hard": (16, 30, 115)}.items():
            tk.Button(bottom_frame, text=difficulty,
                      command=lambda r=r, c=c, m=m: self.change_difficulty(r, c, m)).pack(side=tk.LEFT, padx=5)

    def change_difficulty(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines_count = mines
        self.create_board()

    def create_board(self):
        # 清空旧网格（如果存在）
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.root.winfo_children()[0] and widget != \
                    self.root.winfo_children()[-1]:
                pass

        # 销毁旧按钮并重新生成
        if hasattr(self, 'board_frame') and self.board_frame:
            self.board_frame.destroy()

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(padx=10, pady=5)

        self.grid_buttons = []
        for r in range(self.rows):
            row_buttons = []
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, width=2, height=1, font=("Arial", 10, "bold"),
                                command=lambda r=r, c=c: self.left_click(r, c))
                btn.bind("<Button-3>", lambda event, r=r, c=c: self.right_click(r, c))
                # Mac 用户触摸板支持 Ctrl+左键插旗
                btn.bind("<Control-Button-1>", lambda event, r=r, c=c: self.right_click(r, c))
                btn.grid(row=r, column=c)
                row_buttons.append(btn)
            self.grid_buttons.append(row_buttons)

        self.reset_game()

    def reset_game(self):
        self.is_first_click = True
        self.is_game_over = False
        self.flags_count = 0
        self.revealed_count = 0
        self.start_time = 0
        self.timer_running = False
        self.reset_btn.config(text="🙂")
        self.mine_label.config(text=f"💣 {self.mines_count}")
        self.time_label.config(text="⏱ 000")

        self.mines = []
        self.numbers = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                btn = self.grid_buttons[r][c]
                btn.config(text="", state=tk.NORMAL, bg="SystemButtonFace", relief=tk.RAISED)

    def place_mines(self, first_r, first_c):
        # 确保首点及周围8格无雷
        safe_zone = {(first_r, first_c)}
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                safe_zone.add((first_r + dr, first_c + dc))

        self.mines = []
        while len(self.mines) < self.mines_count:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if (r, c) not in safe_zone and (r, c) not in self.mines:
                self.mines.append((r, c))

        # 计算数字
        for r, c in self.mines:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) not in self.mines:
                        self.numbers[nr][nc] += 1

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time()
            self.update_timer()

    def update_timer(self):
        if self.timer_running and not self.is_game_over:
            elapsed = int(time.time() - self.start_time)
            self.time_label.config(text=f"⏱ {elapsed:03d}")
            self.root.after(1000, self.update_timer)

    def left_click(self, r, c):
        if self.is_game_over or self.revealed[r][c] or self.flagged[r][c]:
            return

        if self.is_first_click:
            self.is_first_click = False
            self.place_mines(r, c)
            self.start_timer()

        self.reveal_cell(r, c)
        self.check_game_state()

    def right_click(self, r, c):
        if self.is_game_over or self.revealed[r][c]:
            return

        if not self.flagged[r][c] and self.flags_count < self.mines_count:
            self.flagged[r][c] = True
            self.grid_buttons[r][c].config(text="🚩", fg="red")
            self.flags_count += 1
            self.mine_label.config(text=f"💣 {self.mines_count - self.flags_count}")
        elif self.flagged[r][c]:
            self.flagged[r][c] = False
            self.grid_buttons[r][c].config(text="")
            self.flags_count -= 1
            self.mine_label.config(text=f"💣 {self.mines_count - self.flags_count}")

    def reveal_cell(self, r, c):
        if self.revealed[r][c] or self.flagged[r][c]:
            return

        self.revealed[r][c] = True
        self.revealed_count += 1
        btn = self.grid_buttons[r][c]
        btn.config(relief=tk.SUNKEN, state=tk.DISABLED)

        if (r, c) in self.mines:
            btn.config(text="💣", bg="red")
            self.game_over()
            return

        # 🛠️ 修复：把 colors 放到函数开头，确保 if 和 else 都能访问
        colors = {1: "blue", 2: "green", 3: "red", 4: "purple", 5: "maroon", 6: "turquoise", 7: "black", 8: "gray"}

        num = self.numbers[r][c]
        if num > 0:
            btn.config(text=str(num), fg=colors.get(num, "black"), disabledforeground=colors.get(num, "black"))
        else:
            # 自动展开周围空白区域（BFS 方式，防止递归深度过大）
            queue = [(r, c)]
            while queue:
                cr, cc = queue.pop(0)
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                                self.revealed[nr][nc] = True
                                self.revealed_count += 1
                                n_btn = self.grid_buttons[nr][nc]
                                n_btn.config(relief=tk.SUNKEN, state=tk.DISABLED)
                                n_num = self.numbers[nr][nc]
                                if n_num > 0:
                                    n_btn.config(text=str(n_num), fg=colors.get(n_num, "black"),
                                                 disabledforeground=colors.get(n_num, "black"))
                                else:
                                    queue.append((nr, nc))

    def check_game_state(self):
        if self.revealed_count == self.rows * self.cols - self.mines_count:
            self.is_game_over = True
            self.timer_running = False
            self.reset_btn.config(text="😎")
            messagebox.showinfo("Congratulation", f"You win！It took {int(time.time() - self.start_time)} seconds.")
            for r, c in self.mines:
                self.grid_buttons[r][c].config(text="🚩", fg="red")

    def game_over(self):
        self.is_game_over = True
        self.timer_running = False
        self.reset_btn.config(text="😵")
        for r, c in self.mines:
            if not self.flagged[r][c]:
                self.grid_buttons[r][c].config(text="💣", state=tk.DISABLED, bg="red")
        messagebox.showerror("Game Over", "You stepped on a landmine!")


if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()