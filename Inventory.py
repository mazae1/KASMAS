import datetime

class Item:
    def __init__(self, name, amount=1, exp_date=None):
        self.name = name #descriptive name of item
        self.amount = amount #keeps track of remaining amount/number

        if isinstance(exp_date, str): #convert exp_date to datetime object if str
            self.exp_date = datetime.datetime.strptime(exp_date, '%Y-%m-%d')
        else: #keep as is if exp_date is datetime obj or None
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

def log_to_file(logfile, item_obj, event_code=0, message=''):
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    with open(logfile, 'a') as f:
        f.write(f'{now}\t{item_obj.name}\t{event_code}\t{message}\n')
        print(f'{now}\t{item_obj.name}\t{event_code}\t{message}\n')

    #event_code:
        #0 = custom event
        #1 = item added
        #2 = item deleted
        #3 = item modified
        #4 = item expired

class Storage:
    def __init__(self, logfile='activity.log'):
        '''
        Params:
            [str] logfile: specifies logfile to store activity
        '''
        self.items = [] #list of currently stored items
        self.logfile = logfile
        
    def __len__(self):
        '''
        Returns: number of stored items
        '''
        return len(self.items)

    def add_item(self, item_obj, log=True):
        '''
        Params:
            [item] item: item to be stored 
            [bool] log: if True logs activity to file
        '''
        self.items.append(item_obj)

        if log:
            log_to_file(self.logfile, item_obj, event_code=1, message='item added to inventory')

    def remove_item(self, item_obj, log=True):
        '''
        Params:
            [item] item: item to be removed
        '''
        if item_obj in self.items:
            self.items.remove(item_obj)

            if log:
                log_to_file(self.logfile, item_obj, event_code=2, message='item removed from inventory')
        else:
            raise ValueError(f'Item {item_obj.name} not found in inventory.')

    def modify_item(self, item_obj, new_amount, log=True):
        '''
        Params:
            [item] item_obj: item to be modified.
        '''
        if item_obj in self.items:
            item_obj.amount = new_amount
            
            if log:
                log_to_file(self.logfile, item_obj, event_code=3, message=f'New amount set to {new_amount}')
        
        else:
            raise ValueError(f'Item {item_obj.name} not found in inventory.')

if __name__ == '__main__':
    milk = Item('milk', exp_date='2025-08-07')
    print('expires in ', milk.expires_in())
    print(milk.is_expired())
    fridge = Storage()
    fridge.add_item(milk)
    fridge.modify_item(milk, .5)
    fridge.remove_item(milk)
