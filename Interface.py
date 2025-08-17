import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import serial
import datetime
from dateutil.relativedelta import relativedelta

class GUI(tk.Tk):
    def __init__(self, config, storage, database, size=(800, 480), fullscreen=True):
        super().__init__()
        self.title('KASMAS')
        self.geometry(f'{size[0]}x{size[1]}')
        self.attributes('-fullscreen', fullscreen)
        self.storage = storage
        self.database = database
        self.config = config

        self.scanner = serial.Serial(port=self.config['serial_port'], baudrate=9600, timeout=.1)

        header = tk.Label(self, text='K A S M A S', font=('Arial', 18, 'bold'))
        header.grid(row=0, column=0, sticky='E', padx=5)
        header_1 = tk.Label(self, text='Inventory system', font=('Arial', 14))
        header_1.grid(row=0, column=1, sticky='W', padx=5)

        self.after(100, self.check_scanner())
        
    def check_scanner(self):
        if self.scanner.in_waiting:
            code = self.scanner.readline().decode(errors='ignore').strip()
            if code:
                self.handle_barcode(code)

        self.after(100, self.check_scanner)

    def add_item_popup(self, code):
        def on_ok():
            import Inventory as inv
            if no_exp_date.get():
                item = inv.Item(name, 1, barcode=code)
            else:
                item = inv.Item(name, 1, exp_date=date, barcode=code)
            self.storage.add_item(item)
            popup.destroy()
            self.refresh_table()
        
        def update_date(delta):
            nonlocal date
            date += delta

            days.set(get_dateval(date, '%d'))
            months.set(get_dateval(date, '%m'))
            years.set(get_dateval(date, '%y'))

        def get_dateval(date, formatter):
            return datetime.datetime.strftime(date, formatter)

        popup = tk.Toplevel(self)

        _, name, cat = self.database.get_item_from_barcode(code)

        date = datetime.datetime.now()
        days = tk.StringVar(value=get_dateval(date, '%d'))
        months = tk.StringVar(value=get_dateval(date, '%m'))
        years = tk.StringVar(value=get_dateval(date, '%y'))

        increment_days_button = tk.Button(popup, text="▲", command=lambda: update_date(relativedelta(days=+1)))
        increment_days_button.grid(row=0, column=0)
        days_label = tk.Label(popup, textvariable=days)
        days_label.grid(row=1, column=0)
        decrement_days_button = tk.Button(popup, text="▼", command=lambda: update_date(relativedelta(days=-1)))
        decrement_days_button.grid(row=2, column=0)

        increment_months_button = tk.Button(popup, text="▲", command=lambda: update_date(relativedelta(months=1)))
        increment_months_button.grid(row=0, column=1)
        months_label = tk.Label(popup, textvariable=months)
        months_label.grid(row=1, column=1)
        decrement_months_button = tk.Button(popup, text="▼", command=lambda: update_date(relativedelta(months=-1)))
        decrement_months_button.grid(row=2, column=1)

        increment_years_button = tk.Button(popup, text="▲", command=lambda: update_date(relativedelta(years=1)))
        increment_years_button.grid(row=0, column=2)
        years_label = tk.Label(popup, textvariable=years)
        years_label.grid(row=1, column=2)
        decrement_years_button = tk.Button(popup, text="▼", command=lambda: update_date(relativedelta(years=-1)))
        decrement_years_button.grid(row=2, column=2)

        no_exp_date = tk.BooleanVar()
        no_date_checkbox = tk.Checkbutton(popup, text='no expiration date', variable=no_exp_date)
        no_date_checkbox.grid(row=3, column=0, columnspan=4)

        ok_button = tk.Button(popup, text='OK', command=on_ok)
        ok_button.grid(row=1, column=3)

    def add_to_database_popup(self, code):

        def on_ok():
            self.database.add_item(code, name.get(), category.get())
            print(f'{name.get()}: {code} added to database.')
            popup.destroy()
            answer = messagebox.askyesno(title='a', message='Add item to inventory?')
            if answer:
                self.add_item_popup(code)

        def on_cancel():
            popup.destroy()

        popup = tk.Toplevel(self)
        name = tk.StringVar()

        name_label = tk.Label(popup, text='Product name:')
        name_entry = tk.Entry(popup, textvariable=name)
        name_label.grid(row=0, column=0)
        name_entry.grid(row=0, column=1)

        category = ttk.Combobox(popup, values=self.config["categories"])
        category.current(0)
        category.grid(row=0, column=2)

        ok_button = tk.Button(popup, text='OK',  command=on_ok)
        ok_button.grid(row=0, column=3)

        cancel_button = tk.Button(popup, text='cancel',  command=on_cancel)
        cancel_button.grid(row=0, column=4)

    def select_item_from_list(self, master, items):

        selected_item = {'val': None}

        if len(items) == 1:
            return items[0]

        def on_click(event):
            uid = tree.identify_row(event.y)
            if uid:
                tree.selection_set(uid)
                selected_item['val'] = self.storage.get_item_from_uid(uid)
                popup.destroy()

        popup = tk.Toplevel(master)
        popup.grab_set()

        tree = ttk.Treeview(popup, columns=('name', 'exp_date'), show='headings')
        tree.heading('name', text='Item')
        tree.heading('exp_date', text='expiration date')
        tree.pack()

        for item in items:
            tree.insert('', 0, iid=item.uid, values=(item.name, item.get_exp_date()))

        tree.bind('<Button-1>', on_click)

        popup.wait_window()

        return selected_item['val']

    def options_menu(self, code):

        in_storage = self.storage.get_items_from_code(code)

        def on_add():
            self.add_item_popup(code)
            popup.destroy()

        def on_remove():
            selected_item = self.select_item_from_list(popup, in_storage)
            answer = messagebox.askokcancel(title='Remove Item', message='Are you sure you want to remove this item?')
            if answer:
                self.storage.remove_item(selected_item)
                self.refresh_table()
            popup.destroy()

        def on_modify():
            selected_item = self.select_item_from_list(popup, in_storage)
            self.modify_menu(selected_item)
            popup.destroy()

        popup = tk.Toplevel(self)

        add_button = tk.Button(popup, text='Add', command=on_add)
        add_button.grid(row=0, column=0)
        remove_button = tk.Button(popup, text='remove', command=on_remove)
        remove_button.grid(row=0, column=1)
        modify_button = tk.Button(popup, text='modify', command=on_modify)
        modify_button.grid(row=0, column=2)

    def handle_barcode(self, code):
        #functiuon to call different functions depending if barcode is in register or not
        if self.database.has_barcode(code):
            #ask further action
            print('scanned item in database')
            in_storage = self.storage.get_items_from_code(code)
            if len(in_storage) >= 1:
                #open options menu
                self.options_menu(code)
                print('in storage')
                pass
            else:
                #jump directly to add item
                self.add_item_popup(code)
                print('not in storage')
                pass
                
        else:
            'add item to inventory'
            self.add_to_database_popup(code)
            #self.database.add_item(code)
            print('scanned item not in database')

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