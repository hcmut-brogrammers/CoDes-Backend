from typing import Any, override

from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database

from ..constants.mongo import CollectionName

IS_DELETED = "is_deleted"
NON_SOFT_DELETE_COLLECTIONS = {CollectionName.REFRESH_TOKENS}


class SoftDeleteCollection(Collection):
    def __init__(self, collection: Collection):
        super().__init__(database=collection._database, name=collection._name, codec_options=collection._codec_options)

    def find_one(self, filter: Any | None = None, *args, **kwargs):
        filter = filter or {}
        if IS_DELETED not in filter:
            filter[IS_DELETED] = False
        return super().find_one(filter, *args, **kwargs)

    def find(self, filter: Any | None = None, *args, **kwargs) -> Cursor:
        filter = filter or {}
        if IS_DELETED not in filter:
            filter[IS_DELETED] = False
        return super().find(filter, *args, **kwargs)


class WrappedDatabase(Database):
    def __init__(self, db: Database):
        super().__init__(client=db._client, name=db._name, codec_options=db._codec_options)

    @override
    def get_collection(
        self,
        name: str,
        codec_options=None,
        read_preference=None,
        write_concern=None,
        read_concern=None,
    ) -> SoftDeleteCollection | Collection:

        raw_collection = super().get_collection(
            name,
            codec_options=codec_options,
            read_preference=read_preference,
            write_concern=write_concern,
            read_concern=read_concern,
        )
        if name in NON_SOFT_DELETE_COLLECTIONS:
            return raw_collection

        return SoftDeleteCollection(raw_collection)
