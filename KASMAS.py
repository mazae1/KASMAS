
from Inventory import *
from Interface import *

storage = Storage()
storage.add_item(Item('milk', exp_date='2025-10-05'))
storage.add_item(Item('cheese', exp_date='2025-11-05'))

database = Database()

app = GUI(storage, database, fullscreen=False)

app.make_item_table()
app.make_scan_menu()
app.run()