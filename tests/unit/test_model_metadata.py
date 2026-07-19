from sqlalchemy.orm import configure_mappers

from app.db.models import Base


def test_catalog_models_are_registered_in_metadata() -> None:
    configure_mappers()

    tables = Base.metadata.tables
    assert {"stores", "tags", "product_tags"}.issubset(tables)
    assert tables["products"].c.store_id.nullable
    assert not tables["products"].c.created_at.nullable
    assert not tables["products"].c.scrape_interval_minutes.nullable
    assert set(tables["product_tags"].primary_key.columns.keys()) == {
        "product_id",
        "tag_id",
    }
