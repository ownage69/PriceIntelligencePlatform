from sqlalchemy.orm import configure_mappers

from app.db.models import Base


def test_catalog_models_are_registered_in_metadata() -> None:
    """Ensure Alembic discovers the new tables and Product relationships."""
    configure_mappers()

    tables = Base.metadata.tables
    assert {"users", "stores", "tags", "product_tags"}.issubset(tables)
    assert tables["products"].c.store_id.nullable
    assert set(tables["product_tags"].primary_key.columns.keys()) == {
        "product_id",
        "tag_id",
    }
