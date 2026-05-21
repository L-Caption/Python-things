import tkinter as tk 
import random 

class Button_Chain_Main:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('TODO')
        self.root.geometry("600x400")
        self.root.resizable(False, True)
        
        self.todo_count = 0
        self.next_id = 1
        self.todo_label1 = tk.Label(self.root, text="задач на сегодня: 0", font=("Arial", 20, 'bold'))
        self.todo_label1.pack(pady=10)

        self.inputer = tk.Entry(
            self.root,
            justify='left', 
            background='#ADD8E6',
            width=45,
            font=("Arial", 12)
        )
        self.inputer.pack(anchor='center', padx=8, pady=8)

        self.addbtn = tk.Button(
            self.root,
            anchor='nw',
            text='Добавить',
            justify='center',
            font=("Arial", 10, 'bold'),
            bg="#4CAF50",
            fg="#FFFFFF",
            activebackground="#53E658",
            relief='raised',
            cursor="hand2",
            command=self.add_init
        )
        self.addbtn.place(x=5, y=25, width=150, height=40)
        
        self.mainframe = tk.Frame(
           bg='#ADD8E6'
        )
        self.mainframe.pack(pady=40, fill='both')
        
        


    def on_click(self, clicked_btn):
        self.todo_count -= 1
        self.todo_label1.config(text=f'задач на сегодня: {self.todo_count}')
        
        for widget in self.mainframe.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget('tag') == 'todo':
                widget.destroy()
                break
        
            
        
    def del_init(self):
        self.todo_count -= 1
        self.todo_label1.config(text=f'задач на сегодня: {self.todo_count}') 
        return
    def delete_todo(self, frame):
        if frame.winfo_exists():
            frame.destroy()
            if self.todo_count > 0:
                self.todo_count -= 1
            self.todo_label1.config(text=f'задач на сегодня: {self.todo_count}')
        return

    def add_init(self):
        text = self.inputer.get().strip()
        if not text:
            return

        todo_id = self.next_id
        self.next_id += 1

        container = tk.Frame(self.mainframe, bg='#E6F2FF', pady=4)
        container.pack(fill='x', padx=8, pady=4)

        lbl = tk.Label(container, text=f"{todo_id}: {text}", anchor='w', bg='#E6F2FF', font=("Arial", 12))
        lbl.pack(side='left', fill='x', expand=True, padx=(6,0))

        del_btn = tk.Button(container, text='Удалить', bg='#FF5252', fg='white', command=lambda f=container: self.delete_todo(f))
        del_btn.pack(side='right', padx=6)

        self.todo_count += 1
        self.todo_label1.config(text=f'задач на сегодня: {self.todo_count}')
        self.inputer.delete(0, 'end')
        return

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = Button_Chain_Main()
    game.run()