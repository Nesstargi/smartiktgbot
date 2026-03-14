from fastapi import Response
from sqlalchemy.orm import Query as ORMQuery


def normalize_search_query(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None


def paginate_query(
    query: ORMQuery,
    response: Response,
    *,
    limit: int | None,
    offset: int,
):
    total = query.order_by(None).count()
    response.headers["X-Total-Count"] = str(total)

    if offset:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    return query.all()
