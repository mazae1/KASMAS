import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import serial
import datetime

class GUI(tk.Tk):
    def __init__(self, storage, database, port, size=(800, 480), fullscreen=True):
        super().__init__()
        self.title('KASMAS')
        self.geometry(f'{size[0]}x{size[1]}')
        self.attributes('-fullscreen', fullscreen)
        self.storage = storage
        self.database = database

        self.scanner = serial.Serial(port=port, baudrate=9600, timeout=.1)

        header = tk.Label(self, text='K A S M A S', font=('Arial', 18, 'bold'))
        header.grid(row=0, column=0, sticky='E', padx=5)
        header_1 = tk.Label(self, text='Inventory system', font=('Arial', 14))
        header_1.grid(row=0, column=1, sticky='W', padx=5)

        self.after(100, self.check_scanner())
        
    def check_scanner(self):
        if self.scanner.in_waiting:
            data = self.scanner.readline().decode(errors='ignore').strip()
            if data:
                self.handle_barcode(data)

        self.after(100, self.check_scanner)

    def handle_barcode(self, data):
        'functiuon to call different functions depending if barcode is in register or not'
        if self.database.has_barcode(data):
            'ask further action'
            print('drinn')

        else:
            'add item to inventory'
            self.database.add_item(data)
            print('ned drinn')

    def make_scan_menu(self):
        font = ('Arial', 14)
        server_button = tk.Button(self, text='Refresh server', font=font)
        server_button.grid(row=1, column=2, sticky='NESW')
        add_button = tk.Button(self, text='Add item', font=font, command=self.add_item_manually)
        add_button.grid(row=2, column=2, sticky='NESW')
        scan_button = tk.Button(self, text='Scan', font=font)
        scan_button.grid(row=3, column=2, sticky='NESW')

    def add_item_manually(self):
        import Inventory as ivt
        popup = tk.Toplevel(self)
        _srg = ivt.Storage()
        _srg.add_item(ivt.Item('milk'), log=False)
        _srg.add_item(ivt.Item('toast'), log=False)
        tree = self.item_treeview(popup, _srg)
        tree.pack()

    def item_treeview(self, master, storage):
        def on_click(event):
            uid = tree.identify_row(event.y)
            if uid:
                tree.selection_set(uid)
        tree = ttk.Treeview(master, columns=('name'), show='headings')
        self.tree.heading('name', text='Item')
        for item in storage:
            tree.insert('', 0, iid=item.uid, values=(item.name))
        tree.bind('<Button-1>', on_click)
        return tree

    def make_item_table(self):
        self.tree = ttk.Treeview(self, columns=('name', 'amount', 'exp. date'), show='headings')
        self.tree.heading('name', text='Item', command=self.namesort)
        self.tree.heading('amount', text='amount', command=self.amountsort)
        self.tree.heading('exp. date', text='expiration date', command=self.datesort)
        for item in self.storage:
            self.tree.insert('', 0, iid=item.uid, values=(item.name, item.amount, item.get_exp_date()))

        self.tree.bind('<Button-1>', self.on_press)
        self.tree.grid(row=1, column=0, columnspan=2, rowspan=3, padx=10)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.storage:
            self.tree.insert('', 0, iid=item.uid, values=(item.name, item.amount, item.get_exp_date()))

    def on_press(self, event):
        uid = self.tree.identify_row(event.y)
        font = ('Arial', 14)
        if uid:
            self.tree.selection_set(uid)
            item = self.storage.get_item_from_uid(uid)

            popup = tk.Menu(self, tearoff=0)
            popup.add_command(label='modify', font=font, command=lambda:self.modify_menu(item))
            popup.add_separator()
            popup.add_command(label='remove', font=font, command=lambda:self.remove_menu(item))
            popup.tk_popup(event.x_root, event.y_root)

    def modify_menu(self, item):
        def update_amt_var(amt):
            new = max(round(amt_var.get() + amt, 2), 0.0)
            amt_var.set(new)

        def add_modify_button(amt, row, col, color = '#FFFFFF'):
            sign = '+' if amt > 0 else ''
            btn = tk.Button(popup, text=sign+str(amt), font=('Arial', 18), background=color, command=lambda:update_amt_var(amt))
            btn.grid(row=row, column=col, sticky='EW', padx=10)

        def on_ok():
            try:
                self.storage.modify_item(item, amt_var.get())
            except ValueError as e:
                answer = messagebox.askokcancel('Delete item?', 'Amount is less than 0. Delete item?')
                if answer:
                    self.storage.remove_item(item)
            self.refresh_table()
            popup.destroy()

        popup = tk.Toplevel(self)
        amt_var = tk.DoubleVar(value=item.amount)
        tk.Label(popup, text='amount = ', font=('Arial', 18)).grid(row=0, column=0, rowspan=2)
        amt_label = tk.Label(popup, textvariable=amt_var, font=('Arial', 28))
        amt_label.grid(row=0, column=1, rowspan=2)

        add_modify_button(0.1, 0, 2, color="#B3FFA9")
        add_modify_button(1, 0, 3, color="#76FF5A")
        add_modify_button(-0.1, 1, 2, color="#EBA4A4")
        add_modify_button(-1, 1, 3, color="#FF7676")

        ok_button = tk.Button(popup, text='OK', font=('Arial', 18), command=on_ok)
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

    def namesort(self):
        items = [(self.tree.set(iid, 'name'), iid) for iid in self.tree.get_children('')]
        items.sort(key=lambda t: t[0].lower())

        for index, (_, iid) in enumerate(items):
            self.tree.move(iid, '', index)

    def datesort(self):
        def get_vals(uid):
            try:
                return self.storage.get_item_from_uid(uid).expires_in()
            except ValueError:
                return float('inf')

        items = [(self.tree.set(iid, 'exp. date'), iid) for iid in self.tree.get_children('')]
        items.sort(key=lambda t: get_vals(t[1]))

        for index, (_, iid) in enumerate(items):
            self.tree.move(iid, '', index)

    def amountsort(self):
        items = [(self.tree.set(iid, 'amount'), iid) for iid in self.tree.get_children('')]
        items.sort(key=lambda t: -float(t[0]))

        for index, (_, iid) in enumerate(items):
            self.tree.move(iid, '', index)