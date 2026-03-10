from .catalog_common import router

# Register handlers in explicit order.
from . import catalog_catalog  # noqa: F401
from . import catalog_promotions  # noqa: F401
from . import catalog_consultation  # noqa: F401

__all__ = ["router"]
