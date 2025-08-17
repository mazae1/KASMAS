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

def onscreen_keyboard(master, entry):
    kb = tk.Toplevel(master)
    kb.transient(master)

    shift_on = tk.BooleanVar(value=False)

    def upper(c):
        if shift_on.get():
            if c in shift_map:
                return shift_map[c]
            else:
                return c.upper()
        else: return c

    def insert_char(c):
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

    def update_keys():
        for r, row in enumerate(keys):
            for c, char in enumerate(row):
                char = upper(char)
                key = tk.Button(kb, text=char, width=3, command=lambda ch=char: insert_char(ch))
                key.grid(row=r, column=c, sticky='NESW')

    update_keys()
    shift_button = tk.Button(kb, text="Shift", command=toggle_shift)
    shift_button.grid(row=4, column=0, columnspan=3, sticky='EW')