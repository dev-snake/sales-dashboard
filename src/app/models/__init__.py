"""SQLAlchemy ORM models — schema per docs/database-design.md."""

from app.database.base import Base
from app.models.brand import Brand
from app.models.calendar import Calendar
from app.models.category import Category
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.product import Product
from app.models.promotion import Promotion
from app.models.region import Region
from app.models.return_ import Return
from app.models.stock_movement import StockMovement
from app.models.store import Store
from app.models.supplier import Supplier

__all__ = [
    "Base",
    "Brand",
    "Calendar",
    "Category",
    "Customer",
    "Employee",
    "Inventory",
    "Order",
    "OrderItem",
    "Payment",
    "Product",
    "Promotion",
    "Region",
    "Return",
    "StockMovement",
    "Store",
    "Supplier",
]

# Tables that receive set_updated_at() trigger (all with updated_at except calendar)
UPDATED_AT_TABLES: tuple[str, ...] = (
    "regions",
    "stores",
    "employees",
    "customers",
    "suppliers",
    "brands",
    "categories",
    "products",
    "promotions",
    "orders",
    "order_items",
    "payments",
    "inventory",
    "stock_movements",
    "returns",
)
