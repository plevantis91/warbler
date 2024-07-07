"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

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
        u2 = User.signup("testuser2", "test2@test.com", "password", None)
        uid2 = 5678
        u2.id = uid2
        db.session.commit()
        
        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        
    def test_user_follows(self):
        """Does following a user work?"""
            
        u1 = User.query.filter_by(username="testuser1").one()
        u2 = User.query.filter_by(username="testuser2").one()
        
        u1.following.append(u2)
        db.session.commit()
        
        self.assertEqual(len(u2.followers), 1)
        self.assertEqual(len(u1.following), 1)
        self.assertEqual(u2.followers[0].id, u1.id)
        self.assertEqual(u1.following[0].id, u2.id)
        
    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        
        u1 = User.query.filter_by(username="testuser1").one()
        u2 = User.query.filter_by(username="testuser2").one()
        
        u1.following.append(u2)
        db.session.commit()
        
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))
        
    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        
        u1 = User.query.filter_by(username="testuser1").one()
        u2 = User.query.filter_by(username="testuser2").one()
        
        u1.following.append(u2)
        db.session.commit()
        
        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u1.is_followed_by(u2))
        
    def test_signup(self):
        """Does User.signup successfully create a new user given valid credentials?"""
        
        new_user = User.signup("testuser3", "test3@test.com", "password", None)
        uid = 6789
        new_user.id = uid
        db.session.commit()
        
        u = User.query.get(uid)
        self.assertIsNotNone(u)
        self.assertEqual(u.username, "testuser3")
        self.assertEqual(u.email, "test3@test.com")
        self.assertNotEqual(u.password, "password")
        self.assertTrue(u.password.startswith("$2b$"))
        
    def authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        
        u = User.authenticate("testuser1", "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, uid1)
        
    def test_bad_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        
        self.assertFalse(User.authenticate("badusername", "password"))
        
    def test_bad_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        
        self.assertFalse(User.authenticate("testuser1", "badpassword"))
        
            
            
