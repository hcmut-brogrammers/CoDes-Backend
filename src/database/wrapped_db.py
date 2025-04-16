from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database


class SoftDeleteCollection:
    def __init__(self, collection: Collection):
        self.collection = collection

    # def find_one(self, filter=None, include_deleted=False, *args, **kwargs):
    def find_one(self, filter=None, *args, **kwargs):
        filter = filter or {}
        # if not include_deleted:
        if not "is_deleted" in filter:
            filter["is_deleted"] = False
        return self.collection.find_one(filter, *args, **kwargs)

    # def find(self, filter=None, include_deleted=False, *args, **kwargs) -> Cursor:
    def find(self, filter=None, *args, **kwargs) -> Cursor:
        filter = filter or {}
        # if not include_deleted:
        if not "is_deleted" in filter:
            filter["is_deleted"] = False
        return self.collection.find(filter, *args, **kwargs)

    # Forward any other attributes/methods to the real collection
    def __getattr__(self, item):
        return getattr(self.collection, item)


class WrappedDatabase:
    def __init__(self, db: Database):
        self._db = db

    def get_collection(self, name, *args, **kwargs) -> SoftDeleteCollection:
        raw_collection = self._db.get_collection(name, *args, **kwargs)
        return SoftDeleteCollection(raw_collection)

    # Forward everything else
    def __getattr__(self, name):
        return getattr(self._db, name)
