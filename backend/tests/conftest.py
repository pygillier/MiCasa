import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import Category, Link


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        pub = Category(name="Public", is_public=True, position=0)
        priv = Category(name="Private", is_public=False, position=1)
        db.session.add_all([pub, priv])
        db.session.flush()
        db.session.add_all([
            Link(category_id=pub.id, label="Open", url="https://a.test", is_public=True,
                 kuma_monitor_id=1),
            Link(category_id=pub.id, label="Hidden", url="https://b.test", is_public=False),
            Link(category_id=priv.id, label="Secret", url="https://c.test", is_public=True),
        ])
        db.session.commit()
        yield app
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authed(client):
    with client.session_transaction() as s:
        s["user"] = {"sub": "1", "email": "me@example.test"}
    return client


H = {"X-Requested-With": "test"}
