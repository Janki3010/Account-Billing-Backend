from typing import List

from app.utils.db import get_db
from app.models.base import BaseModel

class BaseRepository:
    __abstract__ = True

    def __init__(self, model: BaseModel):
        self.__model__ = model

    def save(self, data):
        with get_db() as db:
            db.add(data)
            db.commit()
            db.refresh(data)
            return data

    def save_all(self, data):
        with get_db() as db:
            db.add_all(data)
            db.commit()

            for item in data:
                db.refresh(item)
            return data
        
    def get_by_id(self, id, filters : dict = None) -> BaseModel:
        with (get_db() as db):
            query = db.query(self.__model__).filter(self.__model__.id == id)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.__model__, key) == value)
            return query.first()
        
    def get_by_ids(self, ids):
        with get_db() as db:
            return db.query(self.__model__).filter(self.__model__.id.in_(ids)).all()
        
    def get_all(self, filters: dict = None, order_by: str = None, limit: int = None, offset: int = None):
        with get_db() as db:
            query = db.query(self.__model__)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.__model__, key) == value)
            if order_by is not None:
                query = query.order_by(order_by)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            return query.all()

    def get_by_filters(self, filters: dict, model=None, options=None):
        model = model or self.__model__ # Use provided model, else default to self.model
        with get_db() as db:
            query = db.query(model)
            if options:
                query = query.options(options)
            for key, value in filters.items():
                query = query.filter(getattr(model, key) == value)
            return query.first()

    def update_by_id(self, id, data):
        with get_db() as db:
            db.query(self.__model__).filter(self.__model__.id == id).update(data)
            db.commit()
            return True

    def update_by_filters(self, filters: dict, data: dict):
        with get_db() as db:
            query = db.query(self.__model__)
            for key, value in filters.items():
                query = query.filter(getattr(self.__model__, key) == value)
            query.update(data)
            db.commit()
            return True

    def update(self, model: BaseModel, data: dict):
        with get_db() as db:
            for key, value in data.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            db.commit()
            db.refresh(model)
            return model

    def delete_by_id(self, entity_id):
        with get_db() as db:
            db.query(self.__model__).filter(self.__model__.id == entity_id).delete()
            db.commit()
            return True

    def delete_by_ids(self, ids):
        with get_db() as db:
            db.query(self.__model__).filter(self.__model__.id.in_(ids)).delete()
            db.commit()
            return True

    def delete(self, model: BaseModel):
        with get_db() as db:
            db.delete(model)
            db.commit()
            return True

    def delete_by_filters(self, filters: dict):
        with get_db() as db:
            query = db.query(self.__model__)
            for key, value in filters.items():
                query = query.filter(getattr(self.__model__, key) == value)
            query.delete()
            db.commit()
            return True

    def get_count(self, filters: dict = None):
        with get_db() as db:
            query = db.query(self.__model__)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.__model__, key) == value)
            return query.count()

    def delete_by_ids_model(self, ids: List[str], model) -> None:
        """Delete multiple records by their IDs in a given model."""
        with get_db() as db:
            db.query(model).filter(model.id.in_(ids)).delete(synchronize_session=False)
            db.commit()
