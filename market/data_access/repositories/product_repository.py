from market.data_access.models.models import Product
from market.data_access.repositories.IRepository import IRepository


class ProductRepository(IRepository):
    def __init__(self, db):
        self.db = db

    def find_by_id(self, product_id: int) -> Product:
        return self.db.session.query(Product)\
            .options(self.db.joinedload(Product.types)).filter_by(id=product_id).first()

    def find_all_pageable(self, page, rows_per_page: int = 5):
        return self.db.session.query(Product).order_by(Product.id)\
            .paginate(page=page, per_page=rows_per_page, error_out=False)

    def find_all(self):
        pass

    def create(self, item):
        pass

    def update(self, item):
        pass

    def delete(self, item_id):
        pass
