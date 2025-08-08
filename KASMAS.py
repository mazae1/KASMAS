
from Inventory import *
from Interface import *

storage = Storage()
storage.add_item(Item('milk', exp_date='2025-10-05'))
storage.add_item(Item('cheese', exp_date='2025-11-05'))

app = GUI(storage, fullscreen=False)

app.make_item_table()
app.run()