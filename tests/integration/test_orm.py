from sqlalchemy import text
from domain.order.value_objects import Orderline
from domain.order.entities import Batch
from datetime import date

def test_orderline_mapper_can_load_lines(session):
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
        Orderline("order1", "HEADPHONES", 1),
        Orderline("order2", "MOUSE", 2),
        Orderline("order3", "FLASH", 3),
    ]
    assert session.query(Orderline).all() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = Orderline("order1", "DECORATIVE-LEDS", 3)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(text('SELECT orderid, sku, qty FROM "order_lines"')))
    assert rows == [("order1", "DECORATIVE-LEDS", 3)]


def test_batches(session):
    session.execute(text('INSERT INTO "batches" VALUES ("batch1", "sku1", 100, null)'))
    session.execute(
        text(
            'INSERT INTO "batches" VALUES ("batch2", "sku2", 200, "2025-05-21")'
        )
    )

    expected = [
        Batch("batch1", "sku1", 100, eta=None),
        Batch("batch2", "sku2", 200, eta=date(2025, 5, 21)),

    ]

    assert session.query(Batch).all() == expected
