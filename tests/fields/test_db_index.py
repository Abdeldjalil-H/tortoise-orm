from typing import Any

from tortoise import fields
from tortoise.contrib import test
from tortoise.exceptions import ConfigurationError
from tortoise.indexes import Index


class CustomIndex(Index):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._foo = ""


class TestIndexHashEqual(test.TestCase):
    def test_index_eq(self):
        assert Index(fields=("id",)) == Index(fields=("id",))
        assert CustomIndex(fields=("id",)) == CustomIndex(fields=("id",))
        assert Index(fields=("id", "name")) == Index(fields=["id", "name"])

        assert Index(fields=("id", "name")) != Index(fields=("name", "id"))
        assert Index(fields=("id",)) != Index(fields=("name",))
        assert CustomIndex(fields=("id",)) != Index(fields=("id",))

    def test_index_hash(self):
        assert hash(Index(fields=("id",))) == hash(Index(fields=("id",)))
        assert hash(Index(fields=("id", "name"))) == hash(Index(fields=["id", "name"]))
        assert hash(CustomIndex(fields=("id", "name"))) == hash(CustomIndex(fields=["id", "name"]))

        assert hash(Index(fields=("id", "name"))) != hash(Index(fields=["name", "id"]))
        assert hash(Index(fields=("id",))) != hash(Index(fields=("name",)))

        indexes = {Index(fields=("id",))}
        indexes.add(Index(fields=("id",)))
        assert len(indexes) == 1
        indexes.add(CustomIndex(fields=("id",)))
        assert len(indexes) == 2
        indexes.add(Index(fields=("name",)))
        assert len(indexes) == 3


class TestIndexAlias(test.TestCase):
    Field: Any = fields.IntField

    def test_index_alias(self) -> None:
        kwargs: dict = getattr(self, "init_kwargs", {})
        with self.assertWarnsRegex(
            DeprecationWarning, "`index` is deprecated, please use `db_index` instead"
        ):
            f = self.Field(index=True, **kwargs)
        assert f.index is True
        with self.assertWarnsRegex(
            DeprecationWarning, "`index` is deprecated, please use `db_index` instead"
        ):
            f = self.Field(index=False, **kwargs)
        assert f.index is False
        f = self.Field(db_index=True, **kwargs)
        assert f.index is True
        f = self.Field(db_index=True, index=True, **kwargs)
        assert f.index is True
        f = self.Field(db_index=False, **kwargs)
        assert f.index is False
        f = self.Field(db_index=False, index=False, **kwargs)
        assert f.index is False
        with self.assertRaisesRegex(ConfigurationError, "can't set both db_index and index"):
            self.Field(db_index=False, index=True, **kwargs)
        with self.assertRaisesRegex(ConfigurationError, "can't set both db_index and index"):
            self.Field(db_index=True, index=False, **kwargs)


class TestIndexAliasSmallInt(TestIndexAlias):
    Field = fields.SmallIntField


class TestIndexAliasBigInt(TestIndexAlias):
    Field = fields.BigIntField


class TestIndexAliasUUID(TestIndexAlias):
    Field = fields.UUIDField


class TestIndexAliasChar(TestIndexAlias):
    Field = fields.CharField
    init_kwargs = {"max_length": 10}
