from http import HTTPStatus
from typing import Any

from flask_sqlalchemy import BaseQuery
from werkzeug.exceptions import NotFound

from yacut.exceptions import InvalidAPIUsage


class MyQuery(BaseQuery):
    def first_or_404(self, api: bool = False) -> Any:
        try:
            return super().first_or_404()
        except NotFound:
            if api:
                raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
            raise NotFound