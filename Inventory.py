import datetime
import uuid
import os
import json
import ast

class Item:
    def __init__(self, name, quantity=1, unit=None, added=None, barcode=None, exp_date=None, type=None, category=None, uid=None):

        if uid is None: #create random uid if uid not specified
            uid = uuid.uuid1()
        elif isinstance(uid, str): #convert uid to uuid object if string
            uid = uuid.UUID(uid)
        if isinstance(exp_date, str): #convert exp_date to datetime object if str
            exp_date = datetime.datetime.strptime(exp_date, '%Y-%m-%d')
        if added is None: #set default value for added to now
            added = datetime.datetime.now()
        if isinstance(added, str): #convert added to datetime object if str
            added = datetime.datetime.strptime(added, '%Y-%m-%d')

        self.name = name #descriptive name of item
        self.quantity = quantity #keeps track of remaining amount/number
        self.unit = unit
        self.added = added
        self.barcode = barcode #stores barcode for future reference
        self.type = type
        self.category = category
        self.uid = uid
        self.exp_date = exp_date

    def expires_in(self):
        """
        Params:
            None
        Returns:
            [float] diff: remaining time until expiration in days
        Raises:
            ValueError: if self.exp_date is not set
        """
        if self.exp_date == None:
            raise ValueError('Expiration date not set')

        now = datetime.datetime.now()
        diff = (self.exp_date - now).total_seconds() / 3600 / 24 + 1 #time till expiration in days

        return diff

    def is_expired(self):
        if self.exp_date is None:
            return False
        return datetime.datetime.now() > self.exp_date

    def get_exp_date(self):
        if self.exp_date is not None:
            return datetime.datetime.strftime(self.exp_date, '%Y.%m.%d')
        else:
            return ''

    def to_dict(self):
        out = self.__dict__.copy()
        out['exp_date'] = datetime.datetime.strftime(self.exp_date, format='%Y-%m-%d') if self.exp_date else None
        out['added'] = datetime.datetime.strftime(self.added, format='%Y-%m-%d')
        out['uid'] = str(self.uid)
        return out

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

def log_to_file(logfile, item_obj, event_code=0, message=''):
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    with open(logfile, 'a') as f:
        f.write(f'{now}\t{item_obj.uid}\t{item_obj.name}\t{event_code}\t{message}\n')
        print(f'{now}\t{item_obj.uid}\t{item_obj.name}\t{event_code}\t{message}\n')

    #event_code:
        #0 = custom event
        #1 = item added
        #2 = item deleted
        #3 = item modified
        #4 = item expired


class Storage:
    def __init__(self, logfile='activity.log', storagelog='storage.json'):
        '''
        Params:
            [str] logfile: specifies logfile to store activity
        '''
        self.items = [] #list of currently stored items
        self.logfile = logfile
        self.storagelog = storagelog
        
    def __len__(self):
        '''
        Returns: number of stored items
        '''
        return len(self.items)

    def __getitem__(self, idx):
        return self.items[idx]

    def __iter__(self):
        return iter(self.items)

    def add_item(self, item_obj, log=True):
        '''
        Params:
            [item] item: item to be stored 
            [bool] log: if True logs activity to file
        '''
        self.items.append(item_obj)
        self.dump_to_storagelog()

        if log:
            log_to_file(self.logfile, item_obj, event_code=1, message='item added to inventory')
            log_to_file(self.logfile, item_obj, event_code=3, message=f'quantity set to {item_obj.quantity}')

    def remove_item(self, item_obj, log=True):
        '''
        Params:
            [item] item: item to be removed
        '''
        if item_obj in self.items:
            self.items.remove(item_obj)
            self.dump_to_storagelog()

            if log:
                log_to_file(self.logfile, item_obj, event_code=2, message='item removed from inventory')
        else:
            raise ValueError(f'Item {item_obj.name} not found in inventory.')

    def modify_item(self, item_obj, new_amount, log=True):
        '''
        Params:
            [item] item_obj: item to be modified.
        '''
        if new_amount <= 0:
            raise ValueError('Amount has to be greater than 0')

        if item_obj in self.items:
            item_obj.quantity = new_amount
            self.dump_to_storagelog()
            
            if log:
                log_to_file(self.logfile, item_obj, event_code=3, message=f'quantity changed to {new_amount}')
        
        else:
            raise ValueError(f'Item {item_obj.name} not found in inventory.')

    def get_item_from_uid(self, uid):
        uid = uuid.UUID(uid)
        for item in self:
            if item.uid == uid:
                return item
        raise ValueError(f'Item with uid {uid} not in storage.')

    def get_items_from_code(self, code):
        return [item for item in self if item.barcode == code]

    def dump_to_storagelog(self):
        storage_data = [item.to_dict() for item in self]
        temp_file = self.storagelog + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(storage_data, f, indent=2)

        os.replace(temp_file, self.storagelog)

    def restore_from_storagelog(self):
        with open(self.storagelog, 'r') as f:
            data = json.load(f)
        items = [Item.from_dict(d) for d in data]
        self.items=items
        return

class Database:
    def __init__(self, file='barcode_database.csv'):
        self.file = file
        if not os.path.exists(file):
            with open(self.file, 'w'): pass

    def has_barcode(self, barcode):
        with open(self.file, 'r') as f:
            lines = f.readlines()
            codes = [ast.literal_eval(line.strip())['barcode'] for line in lines]
        if barcode in codes:
            return True
        return False

    def add_item(self, dict):
        with open(self.file, 'a') as f:
            f.writelines(str(dict) + '\n')

    def get_item_from_barcode(self, code):
        with open(self.file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            item_dict = ast.literal_eval(line.strip())
            if item_dict['barcode'] == code:
                return item_dict
        
        raise ValueError(f'{code} not found in database')

if __name__ == '__main__':
    storage = Storage()
    milk = Item('milk', exp_date='2025-08-07')
    print(type(milk.exp_date))
    print(milk.get_exp_date())
    storage.add_item(milk)
    print(type(storage[0].exp_date))
    print(storage[0].get_exp_date())