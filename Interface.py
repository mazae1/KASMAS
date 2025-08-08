import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class GUI(tk.Tk):
    def __init__(self, storage, size=(800, 480), fullscreen=True):
        super().__init__()
        self.title('KASMAS')
        self.geometry(f'{size[0]}x{size[1]}')
        self.attributes('-fullscreen', fullscreen)
        self.storage = storage

    def make_item_table(self):
        self.tree = ttk.Treeview(self, columns=('name', 'amount', 'exp. date'), show='headings')
        self.tree.heading('name', text='Item')
        self.tree.heading('amount', text='amount')
        self.tree.heading('exp. date', text='expiration date')
        for item in self.storage:
            self.tree.insert('', 0, iid=item.uid, values=(item.name, item.amount, item.get_exp_date()))

        self.tree.bind('<Button-1>', self.on_press)
        self.tree.pack()

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.storage:
            self.tree.insert('', 0, iid=item.uid, values=(item.name, item.amount, item.get_exp_date()))

    def on_press(self, event):
        uid = self.tree.identify_row(event.y)
        if uid:
            self.tree.selection_set(uid)
            item = self.storage.get_item_from_uid(uid)

            popup = tk.Menu(self, tearoff=0)
            popup.add_command(label='modify', command=lambda:self.modify_menu(item))
            popup.add_separator()
            popup.add_command(label='remove', command=lambda:self.remove_menu(item))
            popup.tk_popup(event.x_root, event.y_root)

    def modify_menu(self, item):
        def update_amt_var(amt):
            new = max(round(amt_var.get() + amt, 2), 0.0)
            amt_var.set(new)

        def add_modify_button(amt, row):
            sign = '+' if amt > 0 else ''
            btn = tk.Button(popup, text=sign+str(amt), command=lambda:update_amt_var(amt))
            btn.grid(row=row, column=2, sticky='EW')

        def on_ok():
            try:
                self.storage.modify_item(item, amt_var.get())
            except ValueError as e:
                answer = messagebox.askokcancel('Delete item?', 'Amount is less than 0. Delete item?')
                if answer:
                    self.storage.remove_item(item)
            self.refresh_table()

        popup = tk.Toplevel(self)
        amt_var = tk.DoubleVar(value=item.amount)
        tk.Label(popup, text='amount = ').grid(row=0, column=0, rowspan=4)
        amt_label = tk.Label(popup, textvariable=amt_var)
        amt_label.grid(row=0, column=1, rowspan=4)

        add_modify_button(1, 0)
        add_modify_button(0.1, 1)
        add_modify_button(-0.1, 2)
        add_modify_button(-1, 3)

        ok_button = tk.Button(popup, text='OK', command=on_ok)
        ok_button.grid(row=4, column=0, columnspan=3, sticky='EW')

    def remove_menu(self, item):
        answer = messagebox.askokcancel('Delete item?', 'Are you sure you want to delete the item from storage?')
        if answer:
            self.storage.remove_item(item)
            self.refresh_table()
        else:
            print('no delete')

    def run(self):
        self.mainloop()