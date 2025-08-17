
from Inventory import *
from Interface import *
import json

with open('config.json') as cnfgfl:
    config = json.load(cnfgfl)

storage = Storage()

database = Database()

app = GUI(config, storage, database, fullscreen=False)

app.activate_scanner()
app.make_item_table()
app.run()