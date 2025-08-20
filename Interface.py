import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import serial
import datetime
from dateutil.relativedelta import relativedelta
from Keyboard import *
import website_handler as wh

class GUI(tk.Tk):
    def __init__(self, config, storage, database, size=(800, 480)):
        super().__init__()
        self.title('KASMAS')
        self.geometry(f'{size[0]}x{size[1]}')
        self.attributes('-fullscreen', config['fullscreen'])
        self.storage = storage
        self.database = database
        self.config = config
        self.style = ttk.Style()

        self.style.theme_use(self.config['style'])
        self.option_add("*Font", self.config['standard_font'])
        self.style.configure("Treeview.Heading", font=self.config['standard_font'])
        self.style.configure("Treeview", font=self.config['list_font'])

        self.style.configure("TCombobox", arrowsize=30)

    def load_from_storagelog(self):
        try:
            self.storage.restore_from_storagelog()
            try:
                self.refresh_table()
            except AttributeError:
                print('tree update not successful, tree not initialized')
        except FileNotFoundError as e:
            print(f'{self.storage.storagelog} could not be found: {e}')


    def make_popup(self, master, width, height, borderless=False):

        master_x = master.winfo_x()
        master_y = master.winfo_y()
        master_width = master.winfo_width()
        master_height = master.winfo_height()

        x = master_x + (master_width - width) // 2
        y = master_y + (master_height - height) // 4

        popup = tk.Toplevel(master)
        if borderless:
            popup.overrideredirect(True)
        popup.geometry(f'{width}x{height}+{x}+{y}')
        popup.update_idletasks()
        popup.transient(master)
        popup.grab_set()

        return popup


    def show_header(self, **kwargs):
        canvas = tk.Canvas(self, height=30)
        canvas.create_text(0, 0, text="K A S M A S", font=self.config['bold_font'], anchor='nw')
        canvas.create_text(150, 5, text="Inventory system", anchor='nw')
        canvas.grid(**kwargs)

    def activate_scanner(self):
        try: 
            self.scanner = serial.Serial(port=self.config['serial_port'], baudrate=9600, timeout=.1)
        except serial.SerialException as e:
            print(f'An Error occured while initializing Barcode scanner: {e}. Is the COM port set correctly in config.json?')
            self.scanner = None
            return

        self.after(100, self.check_scanner)

    def make_website(self):
        wh.update_website()

        self.after(5000, self.make_website)
        
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
                item_dict['exp_date'] = None
            else:
                item_dict['exp_date'] = date
            
            self.storage.add_item(inv.Item.from_dict(item_dict))
            popup.destroy()
            self.refresh_table()

        def on_cancel():
            popup.destroy()
        
        def update_date(delta):
            nonlocal date
            date += delta

            days.set(get_dateval(date, '%d'))
            months.set(get_dateval(date, '%m'))
            years.set(get_dateval(date, '%Y'))

        def get_dateval(date, formatter):
            return datetime.datetime.strftime(date, formatter)

        item_dict = self.database.get_item_from_barcode(code)

        popup = self.make_popup(self, width=250, height=250)
        frame = tk.Frame(popup)

        no_exp_date = tk.BooleanVar()
        no_date_checkbox = tk.Checkbutton(frame, text='no expiration date', variable=no_exp_date)
        no_date_checkbox.grid(row=0, column=0, columnspan=5)

        date = datetime.datetime.now()
        days = tk.StringVar(value=get_dateval(date, '%d'))
        months = tk.StringVar(value=get_dateval(date, '%m'))
        years = tk.StringVar(value=get_dateval(date, '%Y'))

        def add_date_modifier(type, var, column):
            increment_button = tk.Button(frame, text="▲", command=lambda: update_date(relativedelta(**{type: +1})))
            increment_button.grid(row=1, column=column, sticky="EWNS")
            label = tk.Label(frame, textvariable=var, font=self.config['bold_font'])
            label.grid(row=2, column=column)
            decrement_button = tk.Button(frame, text="▼", command=lambda: update_date(relativedelta(**{type: -1})))
            decrement_button.grid(row=3, column=column, sticky="EWNS")
            if type != "years":
                dot = tk.Label(frame, text=".", font=self.config['bold_font'])
                dot.grid(row=2, column=column+1)

        add_date_modifier("days", days, 0)
        add_date_modifier("months", months, 2)
        add_date_modifier("years", years, 4)

        ok_button = tk.Button(frame, text='OK', command=on_ok,)
        ok_button.grid(row=4, column=0, columnspan=3, pady=5, padx=5, sticky='NESW')
        cancel_button = tk.Button(frame, text='cancel', command=on_cancel)
        cancel_button.grid(row=4, column=3, columnspan=2, pady=5, padx=5, sticky='NESW')

        frame.pack(expand=True)

    def add_to_database_popup(self, code):

        def on_ok():
            item_dict = {
                'barcode': code,
                'name': name.get(),
                'brand': brand.get(),
                'quantity': quantity.get(),
                'unit': unit.get(),
                'category': category.get(),
                'type': type.get()
            }
            self.database.add_item(item_dict)
            print(f'{name.get()}: {code} added to database.')
            popup.destroy()
            answer = messagebox.askyesno(title='a', message='Add item to inventory?')
            if answer:
                self.add_item_popup(code)

        def on_cancel():
            popup.destroy()

        popup = self.make_popup(self, width=800, height=200)
        frame = tk.Frame(popup)

        padding = 5

        name = tk.StringVar()
        brand = tk.StringVar()
        type = tk.StringVar()
        quantity = tk.StringVar(value=1)

        name_label = tk.Label(frame, text='Prod. name:')
        name_entry = tk.Entry(frame, textvariable=name)
        name_entry.bind('<Button-1>', lambda e: onscreen_keyboard(popup, self, name_entry))
        name_label.grid(row=0, column=0, padx=padding, pady=padding)
        name_entry.grid(row=0, column=1, padx=padding, pady=padding)

        brand_label = tk.Label(frame, text='brand:')
        brand_entry = tk.Entry(frame, textvariable=brand)
        brand_entry.bind('<Button-1>', lambda e: onscreen_keyboard(popup, self, brand_entry))
        brand_label.grid(row=1, column=0, padx=padding, pady=padding)
        brand_entry.grid(row=1, column=1, padx=padding, pady=padding)

        type_label = tk.Label(frame, text='Prod. type:')
        type_entry = tk.Entry(frame, textvariable=type)
        type_entry.bind('<Button-1>', lambda e: onscreen_keyboard(popup, self, type_entry))
        type_label.grid(row=2, column=0, padx=padding, pady=padding)
        type_entry.grid(row=2, column=1, padx=padding, pady=padding)

        qty_frame = tk.Frame(frame)

        quantity_label = tk.Label(qty_frame, text='quantity:')
        quantity_entry = tk.Entry(qty_frame, textvariable=quantity, width=5)
        quantity_entry.bind('<Button-1>', lambda e: onscreen_keyboard(popup, self, quantity_entry))
        quantity_label.grid(row=0, column=0, padx=padding, pady=padding)
        quantity_entry.grid(row=0, column=1, padx=padding, pady=padding)

        unit = ttk.Combobox(qty_frame, values=self.config["units"], width=6, style='TCombobox')
        unit.bind('<Button-1>', lambda e: onscreen_keyboard(popup, self, unit))
        unit.current(0)
        unit.grid(row=0, column=3, padx=padding, pady=padding)

        qty_frame.grid(row=3, column=0, columnspan=2)

        cat_label = tk.Label(frame, text='category: ')
        category = ttk.Combobox(frame, values=self.config["categories"])
        category.current(0)
        cat_label.grid(row=4, column=0, padx=padding, pady=padding)
        category.grid(row=4, column=1, padx=padding, pady=padding)

        ok_cancel_frame = tk.Frame(frame)

        ok_button = tk.Button(ok_cancel_frame, text='OK',  command=on_ok, width=25)
        ok_button.grid(row=0, column=0, sticky='EW', padx=padding, pady=padding)

        cancel_button = tk.Button(ok_cancel_frame, text='cancel',  command=on_cancel, width=25)
        cancel_button.grid(row=0, column=1, sticky='EW', padx=padding, pady=padding)

        ok_cancel_frame.grid(row=5, column=0, columnspan=5)
        frame.pack(expand=True)

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

        popup=self.make_popup(master, width=400, height=600)

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

        popup = self.make_popup(self, width=200, height=300)
        frame = tk.Frame(popup)
        padding = 5

        add_button = tk.Button(frame, text='Add', command=on_add)
        add_button.grid(row=0, column=0, sticky='NESW', padx=padding, pady=padding)
        remove_button = tk.Button(frame, text='remove', command=on_remove)
        remove_button.grid(row=1, column=0, sticky='NESW', padx=padding, pady=padding)
        modify_button = tk.Button(frame, text='modify', command=on_modify)
        modify_button.grid(row=2, column=0, sticky='NESW', padx=padding, pady=padding)

        frame.pack(expand=True)

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
            #add item to database if not known
            self.add_to_database_popup(code)
            print('scanned item not in database')

    def make_item_table(self, rows):
        self.tree = ttk.Treeview(self, columns=('name', 'quantity', 'unit', 'exp. date', 'brand'), show='headings', height=rows)

        self.tree.heading('name', text='Item', command=self.namesort)
        self.tree.heading('quantity', text='amnt', command=self.amountsort)
        self.tree.heading('unit', text='unit', command=self.namesort)
        self.tree.heading('exp. date', text='exp. date', command=self.datesort)
        self.tree.heading('brand', text='brand', command=self.namesort)

        self.tree.column('name', width=200)
        self.tree.column('quantity', width=70)
        self.tree.column('unit', width=60)
        self.tree.column('exp. date', width=150)
        self.tree.column('brand', width=150)

        for item in self.storage:
            self.tree.insert('', 0, iid=item.uid, values=(item.name, item.quantity, item.unit if item.unit else '', item.get_exp_date()))

        self.tree.bind('<Button-1>', self.on_press)

    def show_item_table(self, **kwargs):
        self.tree.grid(**kwargs)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.storage:
            self.tree.insert('', 0, iid=item.uid, values=(item.name, item.quantity, item.unit, item.get_exp_date()))

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
        popup.transient(self)
        popup.grab_set()

        amt_var = tk.DoubleVar(value=item.quantity)
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
        items = [(self.tree.set(iid, 'quantity'), iid) for iid in self.tree.get_children('')]
        items.sort(key=lambda t: -float(t[0]))

        for index, (_, iid) in enumerate(items):
            self.tree.move(iid, '', index)