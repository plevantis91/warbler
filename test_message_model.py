import os 
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        
        u1 = User.signup("testuser1", "test1@test.com", "password", None)
        uid1 = 1234
        u1.id = uid1
        u2 = User.signup("testuser2", "test2@test.com ", "password", None)
        uid2 = 5678
        u2.id = uid2
        db.session.commit()

        self.client = app.test_client()
        
    def tearDown(self) -> None:
        db.session.rollback()
        return super().tearDown

    def test_message_model(self):
        """Does basic model work?"""
        msg = Message(
            text="test message",
            user_id=1234
        )
        db.session.add(msg)
        db.session.commit()
        
        self.assertEqual(len(User.query.get(1234).messages), 1)
        self.assertEqual(User.query.get(1234).messages[0].text, "test message")
        
    def test_message_likes(self):
        """Does the likes work?"""
        msg = Message(
            text="test message",
            user_id=1234
        )
        db.session.add(msg)
        db.session.commit()
        
        u = User.query.get(5678)
        u.likes.append(msg)
        db.session.commit()
        
        self.assertEqual(len(u.likes), 1)
        self.assertEqual(u.likes[0].text, "test message")
        
    def test_message_invalid_user(self):
        """Does the message require a valid user?"""
        with self.assertRaises(IntegrityError):
            msg = Message(
                text="test message",
                user_id=9999
            )
            db.session.add(msg)
            db.session.commit()
            
        
        

    