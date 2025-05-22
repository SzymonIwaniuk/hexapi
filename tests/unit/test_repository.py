# pylint: disable=protected-access
from domain.order.entities import Batch
from domain.order.value_objects import OrderLine
from sqlalchemy import text
from sqlalchemy.orm.session import Session
import repository


def test_repository_can_save_a_batch(session: Session) -> None:
    batch = Batch("batch1", "PROFESSIONAL KEYBOARD", 1, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(
        text(
            'SELECT reference, sku, _purchased_quantity,'
            ' eta FROM "batches"'
        )
    )

    assert list(rows) == [("batch1", "PROFESSIONAL KEYBOARD", 1, None)]


def insert_order_line(session: Session) -> int:
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty)"
            ' VALUES ("order1", "EARPADS", 2)'
        )
    )

    [[orderline_id]] = session.execute(
        text(
            "SELECT id FROM order_lines WHERE "
            "orderid=:orderid AND sku=:sku"
        ),
        dict(orderid="order1", sku="EARPADS"),
    )

    return orderline_id


def insert_batch(session: Session, batch_id: int) -> int:
    session.execute(
        text(
            "INSERT INTO batches "
            "(reference, sku, _purchased_quantity, eta)"
            ' VALUES (:batch_id, "EARPADS", 2, null)',
        ),
        dict(batch_id=batch_id),
    )

    [[batch_id]] = session.execute(
        text(
            'SELECT id FROM batches WHERE '
            'reference=:batch_id AND sku="EARPADS"'
        ),
        dict(batch_id=batch_id),
    )

    return batch_id


def insert_allocation(session: Session, orderline_id: int, batch_id: int) -> None:
    session.execute(
        text(
            "INSERT INTO allocations (orderline_id, batch_id)"
            " VALUES (:orderline_id, :batch_id)",
        ),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(session: Session) -> None:
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = Batch("batch1", "EARPADS", 2, eta=None)
    # Batch.__eq__ only compares reference
    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        OrderLine("order1", "EARPADS", 2),
    }
