import tkinter as tk
from game import GameApp


def main():
    root = tk.Tk()
    GameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()