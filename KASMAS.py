
from Inventory import *
from Interface import *
import json

with open('config.json') as cnfgfl:
    config = json.load(cnfgfl)

storage = Storage()

database = Database()

app = GUI(config, storage, database)
app.load_from_storagelog()

app.activate_scanner()
app.make_website()
app.show_header(row=0, column=0)
app.make_item_table(rows=15)
app.show_item_table(row=1, column=0, sticky='NS')
app.run()