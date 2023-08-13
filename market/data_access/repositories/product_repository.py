from market.data_access.models.models import Product


class ProductRepository:
    def __init__(self, db):
        self.db = db

    def find_by_id(self, product_id: int) -> Product:
        return self.db.session.query(Product)\
            .options(self.db.joinedload(Product.types)).filter_by(id=product_id).first()

    def find_all(self, page, rows_per_page: int = 5):
        return self.db.session.query(Product).order_by(Product.id).paginate(page=page, per_page=rows_per_page)
