import json
from decimal import Decimal
from datetime import date, datetime, timezone
from aiopg.sa.result import RowProxy


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            if obj.tzinfo is None:
                return obj.replace(tzinfo=timezone.utc).isoformat()
            else:
                return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, RowProxy):
            return dict(obj)
        return super().default(obj)
