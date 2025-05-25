from sqlalchemy import text
from domain.model import Batch, OrderLine
from datetime import date


def test_orderline_mapper_can_load_lines(session) -> None:
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty) VALUES "
            '("order1", "HEADPHONES", 1),'
            '("order2", "MOUSE", 2),'
            '("order3", "FLASH", 3)'
        )
    )

    session.commit()

    expected = [
        OrderLine("order1", "HEADPHONES", 1),
        OrderLine("order2", "MOUSE", 2),
        OrderLine("order3", "FLASH", 3),
    ]
    assert session.query(OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session) -> None:
    new_line = OrderLine("order1", "DECORATIVE-LEDS", 3)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(text('SELECT orderid, sku, qty FROM "order_lines"')))
    assert rows == [("order1", "DECORATIVE-LEDS", 3)]


def test_retrieving_batches(session) -> None:
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            ' VALUES ("batch1", "sku1", 100, null)'
        )
    )

    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            ' VALUES ("batch2", "sku2", 200, "2025-05-21")'
        )
    )

    expected = [
        Batch("batch1", "sku1", 100, eta=None),
        Batch("batch2", "sku2", 200, eta=date(2025, 5, 21)),

    ]

    assert session.query(Batch).all() == expected


def test_saving_batches(session) -> None:
    batch = Batch("batch1", "sku1", 100, eta=None)
    session.add(batch)
    session.commit()

    rows = session.execute(
                text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
                )

    assert list(rows) == [("batch1", "sku1", 100, None)]


def test_saving_allocations(session) -> None:
    batch = Batch("batch1", "sku1", 100, eta=None)
    line = OrderLine("order1", "sku1", 10)
    batch.allocate(line)
    session.add(batch)
    session.commit()

    rows = list(session.execute(
        text(
            'SELECT orderline_id, batch_id FROM "allocations"')
        )
    )

    assert rows == [(batch.id, line.id)]


def test_retrieving_allocations(session) -> None:
    session.execute(
        text(
            'INSERT INTO order_lines (orderid, sku, qty) VALUES ("order1", "sku1", 12)'
        )
    )

    [[olid]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid="order1", sku="sku1"),
    )

    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
            'VALUES ("batch1", "sku1", 100, null)'
        )
    )

    [[bid]] = session.execute(
        text("SELECT id FROM batches WHERE reference=:ref AND sku=:sku"),
        dict(ref="batch1", sku="sku1"),
    )

    session.execute(
        text("INSERT INTO allocations (OrderLine_id, batch_id) VALUES (:olid, :bid)"),
        dict(olid=olid, bid=bid),
    )

    batch = session.query(Batch).one()

    assert batch._allocations == {OrderLine("order1", "sku1", 12)}
