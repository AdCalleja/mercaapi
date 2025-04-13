from datetime import datetime, timedelta
from typing import Any, List

from loguru import logger
from sqlmodel import select, Session
from sqlalchemy.orm import joinedload

from app.models import Product, NutritionalInformation


class Cache:
    def __init__(self, timeout: int = 3600):
        self.data: dict[str, Any] = {}
        self.timeout = timeout

    def get(self, key: str):
        if key in self.data:
            value, timestamp = self.data[key]
            if datetime.now() - timestamp < timedelta(seconds=self.timeout):
                return value
        return None

    def set(self, key: str, value: Any):
        self.data[key] = (value, datetime.now())


cache = Cache()


def get_all_products(session: Session) -> List[Product]:
    cached_products = cache.get("all_products")
    if cached_products:
        logger.debug("Retrieved products from cache")
        return cached_products

    logger.debug("Fetching all products from database")
    products = (
        session.exec(
            select(Product).options(
                joinedload(Product.category),  # type: ignore
                joinedload(Product.images),  # type: ignore
                joinedload(Product.nutritional_information),  # type: ignore
                joinedload(Product.price_history),  # type: ignore
            )
        )
        .unique()
        .all()
    )

    # Detach products from the session
    for product in products:
        session.expunge(product)

    cache.set("all_products", products)
    return list(products)


def get_products_with_protein_from_db(session: Session) -> List[Product]:
    """Get products that have nutritional information with non-zero protein content."""
    logger.debug("Fetching products with protein from database")
    products = (
        session.exec(
            select(Product)
            .join(Product.nutritional_information)
            .where(
                NutritionalInformation.protein.is_not(None),
                NutritionalInformation.protein > 0
            )
            .options(
                joinedload(Product.category),  # type: ignore
                joinedload(Product.images),  # type: ignore
                joinedload(Product.nutritional_information),  # type: ignore
                joinedload(Product.price_history),  # type: ignore
            )
        )
        .unique()
        .all()
    )

    # Detach products from the session
    for product in products:
        session.expunge(product)

    return list(products)
