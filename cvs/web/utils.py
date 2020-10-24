import json
from decimal import Decimal
from datetime import date, datetime
from aiopg.sa.result import RowProxy


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, RowProxy):
            return dict(obj)
        return super().default(obj)
