import inspect
import pandas as pd
from .utils import to_snake, Schema, hydrate


class Model:
    pk: int = 0

    def __init__(self, *args, **kwargs):
        self._schema = Schema(self)
        self.__dict__.update(self._schema.values)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def _snake_name(self) -> str:
        return to_snake(self.__class__.__name__)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def _as_response(self, df, db):
        return hydrate(self.__class__, df, db)

    def _to_dict(self) -> dict:
        fields_dict = dict()
        for field, dtype, default_value in self._schema.items():
            if inspect.isclass(default_value):
                default_value = 0
            elif dtype == list:
                default_value = list()
            elif dtype == set:
                default_value = set()

            fields_dict[field] = default_value

        instance_values = self.__dict__
        for field, value in instance_values.items():
            if field[0] == "_":
                continue
            fields_dict[field] = value

        return fields_dict

    def _to_df(self) -> pd.DataFrame:
        df = pd.DataFrame([self._to_dict()])
        return df

    def _on_read(self, db):
        return self._to_df()

    def _on_create(self, db):
        table_name = to_snake(self.__class__.__name__)
        self.pk = db.new_pk(table_name)
        return self._to_df()

    def _on_change(self, db):
        return self._to_df()

    def _on_delete(self, db):
        return self._to_df()

    def __repr__(self):
        return self._to_df().to_string()

class ModelManager:
    def __init__(self, models: list):
        self.__models__ = models
        for model in models:
            self.__dict__[model.__name__] = model

    def __iter__(self):
        for model in self.__models__:
            yield model

    def __getitem__(self, index: int):
        return self.__models__[index]
