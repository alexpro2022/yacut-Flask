from datetime import datetime as dt
from typing import Dict, Tuple

from flask_sqlalchemy import SQLAlchemy

from yacut import db
from yacut.exceptions import InvalidAPIUsage
from yacut.queries import MyQuery
from yacut.settings import (API_ORIGINAL_REQUEST, API_ORIGINAL_RESPONSE,
                            API_SHORT_REQUEST, API_SHORT_RESPONSE, BASE_URL,
                            CUSTOM_ID_SIZE_MANUAL, FORM_ORIGINAL, FORM_SHORT,
                            LINK_SIZE_MAX, a_zA_Z0_9)
from yacut.utils import get_invalid_symbols, get_unique_id, is_exist


class TimestampMixin:
    timestamp = db.Column(db.DateTime, default=dt.utcnow)


class ModelPK(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


class URLMap(TimestampMixin, ModelPK):
    query_class = MyQuery
    original = db.Column(
        db.String(LINK_SIZE_MAX),
        nullable=False,
    )
    short = db.Column(
        db.String(CUSTOM_ID_SIZE_MANUAL),
        unique=True,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f'id: {self.id}\n'
            f'original: {self.original}\n'
            f'short: {self.short}\n'
            f'timestamp: {self.timestamp}\n'
        )

    @classmethod
    def get_original_link(cls, short_id: str, api: bool = True) -> str:
        return cls.query.filter_by(short=short_id).first_or_404(api).original

    @classmethod
    def __clean_data(cls, data: Dict[str, str], post: bool = False) -> Tuple[str, str]:
        if not data:
            raise InvalidAPIUsage('Отсутствует тело запроса')
        original = data.get(API_ORIGINAL_REQUEST)
        short = data.get(API_SHORT_REQUEST)
        if post and not original:
            raise InvalidAPIUsage(f'"{API_ORIGINAL_REQUEST}" является обязательным полем!')
        if not short:
            short = get_unique_id(cls, cls.short)
        elif len(short) > CUSTOM_ID_SIZE_MANUAL or get_invalid_symbols(a_zA_Z0_9, short):
            raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
        is_exist(cls, cls.short, short, InvalidAPIUsage(f'Имя "{short}" уже занято.'))
        return original, short

    def to_intenal_value(self, data: Dict[str, str], clean: bool = True, post: bool = False):
        if clean:
            self.original, self.short = self.__class__.__clean_data(data, post)
        else:
            self.original = data[FORM_ORIGINAL]
            self.short = data[FORM_SHORT]
        return self

    def create(self, db: SQLAlchemy, data: Dict[str, str], validation: bool = True):
        db.session.add(self.to_intenal_value(data, clean=validation, post=True))
        db.session.commit()
        return self

    def to_representation(self) -> Dict[str, str]:
        return {
            API_ORIGINAL_RESPONSE: self.original,
            API_SHORT_RESPONSE: f'{BASE_URL}/{self.short}',
        }