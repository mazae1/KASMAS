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

def onscreen_keyboard(master, display_ref, entry):
    master_x = display_ref.winfo_x()
    master_y = display_ref.winfo_y()
    master_width = display_ref.winfo_width()
    master_height = display_ref.winfo_height()

    width = master_width
    height = 200
    x = master_x
    y = master_y + master_height - height

    kb = tk.Toplevel(master)
    kb.geometry(f'{width}x{height}+{x}+{y}')
    kb.update_idletasks()

    shift_on = tk.BooleanVar(value=False)

    key_frame = tk.Frame(kb)

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
                key = tk.Button(key_frame, text=char, width=3, command=lambda ch=char: insert_char(ch), font=font)
                key.grid(row=r, column=c, sticky='NESW')

    def delete_char():
        inside = entry.get()
        if inside:
            entry.delete(len(inside)-1, tk.END)

    update_keys()

    shift_button = tk.Button(key_frame, text="Shift", command=toggle_shift, font=font)
    shift_button.grid(row=4, column=0, columnspan=3, sticky='EW')

    space_bar = tk.Button(key_frame, text=' ', command=lambda: insert_char(' '), font=font)
    space_bar.grid(row=4, column=3, columnspan=5, sticky='EW')

    backspace = tk.Button(key_frame, text='<--', command=delete_char, font=font)
    backspace.grid(row=4, column=8, columnspan=2, sticky='EW')

    close_btn = tk.Button(key_frame, text='close', command=kb.destroy, font=font)
    close_btn.grid(row=3, column=10, rowspan=2, sticky="NESW")

    key_frame.pack(expand=True)

    def click_outside(event):
        if event.widget not in (entry, kb) and not str(event.widget).startswith(str(kb)):
            kb.destroy()
            master.unbind('<Button-1>', binding)

    binding = master.bind('<Button-1>', click_outside, add='+')