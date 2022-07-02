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

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        
    
    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()
            

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        self.user = u
        self.id = u.id
        self.username = u.username
        self.email = u.email
        
        self.repr = u.__repr__

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.likes), 0)
        
        self.assertEqual(self.repr, u.__repr__)

        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD_TWO",
            image_url='/static/images/default-pic.png'
        )

        """ u2 = User.signup(u2.username,u2.email,u2.password,u2.image_url) """
        
        """ db.session.add(u2) """
        db.session.commit()

        self.assertEqual(u2, u2)
        
        self.assertNotEqual(User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD_TWO",
            image_url='/static/images/default-pic.png'
        ), u2)

        self.assertFalse(self.user.is_following(u2))
        self.assertFalse(self.user.is_followed_by(u2))

        following = Follows(
            user_being_followed_id=u2.id,
            user_following_id=self.id
        )

        db.session.add(following)
        db.session.commit()

        self.assertTrue(self.user.is_following(u2))
        self.assertTrue(u2.is_followed_by(self.user))

        good_auth = User.authenticate(u2.username, "HASHED_PASSWORD_TWO")
        bad_auth_pass = User.authenticate(u2.username, "NOTU2PASSWORD")
        bad_auth_username = User.authenticate('NONEEXISTENT USERNAME', "HASHED_PASSWORD_TWO")
        

        self.assertEqual(good_auth, u2)
        self.assertFalse(bad_auth_pass)
        self.assertFalse(bad_auth_username)



        





        


