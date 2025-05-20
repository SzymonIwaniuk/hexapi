from sqlalchemy import text
from domain.order.value_objects import Orderline


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
