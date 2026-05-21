import tkinter as tk 
import random 

class Button_Chain_Main:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('с левой по кнопке, а то чо она')
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.click_count = 0
        self.score_label = tk.Label(self.root, text="кликов: 0", font=("Arial", 20, 'bold'))
        self.score_label.pack(pady=10)
        
        self.create_button(250, 150)

    def create_button(self, x, y):
        btn = tk.Button(
            self.root,
            text='выстрели в меня',
            font=("Arial", 10, 'bold'),
            bg="#4CAF50",
            fg="#FFFFFF",
            activebackground="#53E658",  # <-- исправлено
            relief='raised',
            cursor="hand2"
        )
        btn.place(x=x, y=y, width=120, height=40)
        btn.config(command=lambda b=btn: self.on_click(b))

    def on_click(self, clicked_btn):
        self.click_count += 1
        self.score_label.config(text=f'кликов: {self.click_count}')  # <-- добавлен пробел для читаемости
        
        max_x = 600 - 120 - 10
        max_y = 400 - 40 - 60
        new_x = random.randint(10, max_x)   # <-- исправлено
        new_y = random.randint(60, max_y)   # <-- исправлено
        self.create_button(new_x, new_y)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = Button_Chain_Main()  # <-- добавлены скобки
    game.run()