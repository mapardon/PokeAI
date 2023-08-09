import os
import pickle


class Storage:
    """ The idea was to use a simple serialization system as shelve, but it is unfortunately not cross-platform
     then something similar using pickle is defined here """

    def __init__(self, path):
        self.storage_path = path
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'wb') as db:
                pickle.dump(dict(), db)

    def __setitem__(self, key, value):
        with open(self.storage_path, 'rb') as db:
            storage = pickle.load(db)
        storage[key] = value
        with open(self.storage_path, 'wb') as db:
            pickle.dump(storage, db)

    def __getitem__(self, item):
        with open(self.storage_path, 'rb') as db:
            storage = pickle.load(db)
        return storage[item]

    def __delitem__(self, key):
        with open(self.storage_path, 'rb') as db:
            storage = pickle.load(db)
        del storage[key]
        with open(self.storage_path, 'wb') as db:
            pickle.dump(storage, db)

    def __contains__(self, key):
        return key in self.keys()

    def keys(self):
        with open(self.storage_path, 'rb') as db:
            buf = pickle.load(db)
        return tuple([k for k in buf.keys()])
