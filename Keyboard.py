import tkinter as tk

keys = [
    ['1','2','3','4','5','6','7','8','9','0','ß'],
    ['q','w','e','r','t','y','u','i','o','p','ü'],
    ['a','s','d','f','g','h','j','k','l','ö','ä'],
    ['z','x','c','v','b','n','m',',','.','-']
]

shift_map = {
    '1': '!',
    '2': '"',
    '3': '§',
    '4': '$',
    '5': '%',
    '6': '&',
    '7': '/',
    '8': '(',
    '9': ')',
    '0': '=',
    'ß': '?',
    ',': ';',
    '.': ':',
    '-': '_'
}

font = ('Helvetica', 15)

def onscreen_keyboard(master, entries, custom_func=None, custom_txt=''):

    kb = tk.Frame(master)

    shift_on = tk.BooleanVar(value=False)
    active_entry = [None]

    key_frame = tk.Frame(kb)

    for e in entries:
        e.bind("<FocusIn>", lambda event, lst=active_entry, entry=e: lst.__setitem__(0, entry))

    for e in entries:
        e.bind("<FocusOut>", lambda event: active_entry.__setitem__(0, None) )

    def upper(c):
        if shift_on.get():
            if c in shift_map:
                return shift_map[c]
            else:
                return c.upper()
        else: return c

    def insert_char(c):
        entry = active_entry[0]
        if not entry:
            return
        if shift_on.get():
            entry.insert(tk.END, c.upper())
            shift_on.set(False)
            update_shift()
            update_keys()
        else:
            entry.insert(tk.END, c)

    def update_shift():
        if shift_on.get():
            shift_button.configure(bg="lightblue")
        else:
            shift_button.configure(bg="white")

    def toggle_shift():
        shift_on.set(not shift_on.get())
        update_shift()
        update_keys()

    def make_insert(c):
        return lambda: insert_char(c)

    def update_keys():
        for r, row in enumerate(keys):
            for c, char in enumerate(row):
                char = upper(char)
                key = tk.Button(key_frame, text=char, width=3, command=make_insert(char), font=font)
                key.grid(row=r, column=c, sticky='NESW')

    def delete_char():
        entry = active_entry[0]
        if not entry:
            return
        inside = entry.get()
        if inside:
            entry.delete(len(inside)-1, tk.END)

    key_frame = tk.Frame(kb)
    key_frame.pack(expand=True)

    update_keys()

    shift_button = tk.Button(key_frame, text="Shift", command=toggle_shift, font=font)
    shift_button.grid(row=4, column=0, columnspan=3, sticky='EW')

    space_bar = tk.Button(key_frame, text=' ', command=lambda: insert_char(' '), font=font)
    space_bar.grid(row=4, column=3, columnspan=5, sticky='EW')

    backspace = tk.Button(key_frame, text='<--', command=delete_char, font=font)
    backspace.grid(row=4, column=8, columnspan=2, sticky='EW')

    custom_button = tk.Button(key_frame, text=custom_txt, command=custom_func, font=font)
    custom_button.grid(row=3, column=10, rowspan=2, sticky="NESW")

    key_frame.pack(expand=True)

    return kb