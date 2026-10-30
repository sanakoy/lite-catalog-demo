from sqlalchemy import Column, Enum, Integer, MetaData, String, Table
from sqlalchemy.orm import registry

from lite_catalog_demo import model

metadata = MetaData()
mapper_registry = registry(metadata=metadata)


def status_values(enum_class: type[model.LotStatus]) -> list[str]:
    return [member.value for member in enum_class]


lots = Table(
    "lots",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("number", String(10), unique=True, nullable=False),
    Column("price", Integer, nullable=False),
    Column("rooms", Integer, nullable=False),
    Column(
        "status", Enum(model.LotStatus, values_callable=status_values), nullable=False
    ),
    Column("client", String(100)),
)


def start_mappers() -> None:
    mapper_registry.map_imperatively(model.Lot, lots)
