#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="testuser@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id
        
        self.u1 = User.signup("bob", "bob@test.com", "password", None)
        self.u1_id = 5678
        self.u1.id = self.u1_id
        self.u2 = User.signup("tom", "tom@test.com", "password", None)
        self.u2_id = 91011
        self.u2.id = self.u2_id
        
        db.session.commit()
        
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")
            
            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@bob", str(resp.data))
            self.assertIn("@tom", str(resp.data))
    
    def test_users_search(self):
        with self.client as c:
            resp = c.get("/users?q=bob")
            
            self.assertIn("@bob", str(resp.data))
            self.assertNotIn("@testuser", str(resp.data))
            self.assertNotIn("@tom", str(resp.data))
            
    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")
            self.assertEqual(resp.status_code, 200)
            
            self.assertIn("@testuser", str(resp.data))
            
    def test_user_show_following(self):
        self.testuser.following.append(self.u1)
        db.session.commit()
        
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/following")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@bob", str(resp.data))
            self.assertNotIn("@tom", str(resp.data))
    
    def test_user_show_followers(self):
        self.testuser.followers.append(self.u1)
        db.session.commit()
        
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/followers")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@bob", str(resp.data))
            self.assertNotIn("@tom", str(resp.data))
    
    def test_add_follow(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
                
            resp = c.post(f"/users/follow/{self.u1_id}", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            
            u = User.query.get(self.testuser_id)
            u2 = User.query.get(self.u1_id)
            self.assertIn(u2, u.following)
            
    def test_stop_following(self):
        self.testuser.following.append(self.u1)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
                
            resp = c.post(f"/users/stop-following/{self.u1_id}", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            
            u = User.query.get(self.testuser_id)
            u2 = User.query.get(self.u1_id)
            self.assertNotIn(u2, u.following)
    
    def test_show_following_logged_out(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            
    def test_show_followers_logged_out(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            
    def test_add_follow_logged_out(self):
        with self.client as c:
            resp = c.post(f"/users/follow/{self.u1_id}", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
    
    def test_stop_following_logged_out(self):
        with self.client as c:
            resp = c.post(f"/users/stop-following/{self.u1_id}", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            
    def test_user_search_logged_out(self):
        with self.client as c:
            resp = c.get("/users?q=bob", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            
    def test_user_show_logged_out(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            
        
        
        
        
        
