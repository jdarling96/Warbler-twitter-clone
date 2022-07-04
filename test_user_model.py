"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc


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
    """Test model for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD_TWO",
            image_url='/static/images/default-pic.png'
        )

        db.session.add_all([u,u2])
        db.session.commit()
        
        self.user = u
        self.id = u.id
        self.username = u.username
        self.email = u.email
        self.repr = u.__repr__
        
        self.u2 = u2
        self.id2 = u2.id
        self.username2 = u2.username
        self.email2 = u2.email
        
        

        self.client = app.test_client()

        
    
    def tearDown(self):
        """Clean up any fouled transaction."""
        res = super().tearDown()
        db.session.rollback()
        return res
            

    def test_user_model(self):
        """Does basic model work?"""

       # User should have no messages & no followers
        self.assertEqual(len(self.user.messages), 0)
        self.assertEqual(len(self.user.followers), 0)
        self.assertEqual(len(self.user.likes), 0)
        
        self.assertEqual(self.repr, self.user.__repr__)

        
    def test_user_model_following(self):
        """Test user can follow other users"""

        self.assertFalse(self.user.is_following(self.u2))
        self.assertFalse(self.user.is_followed_by(self.u2))

        following = Follows(
            user_being_followed_id=self.id,
            user_following_id=self.id2
        )

        db.session.add(following)

        db.session.commit()    
        
        
        self.assertTrue(self.u2.is_following(self.user))
        self.assertTrue(self.user.is_followed_by(self.u2))
        self.assertEqual(len(self.u2.following), 1)
        self.assertEqual(len(self.user.followers), 1)
        self.assertEqual(self.u2.following[0], self.user)
    
    def test_user_model_follows(self):
        """Test user can be followed by other users"""

        self.assertFalse(self.u2.is_followed_by(self.user))

        follow = Follows(
            user_being_followed_id=self.id2,
            user_following_id=self.id
        )
        db.session.add(follow)

        db.session.commit()

        self.assertTrue(self.user.is_following(self.u2))
        self.assertTrue(self.u2.is_followed_by(self.user))
        self.assertEqual(len(self.user.following), 1)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(self.u2.followers[0], self.user)




       
    def test_user_model_valid_signup(self):
        """Test users signup functionality with correct criteria met"""
        
        
        
        signup_test = User.signup(
             email="signuptest@email.com",
             username="signuptest",
             password="HASHED_PASSWORD",
             image_url='/static/images/default-pic.png')

        test_id = 99999
        signup_test.id = test_id     
        db.session.commit()

        query_test = User.query.get(signup_test.id)
        self.assertIsNotNone(query_test)
        self.assertEqual(signup_test.username, "signuptest")
        self.assertEqual(signup_test.email, "signuptest@email.com")
        self.assertNotEqual(signup_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(signup_test.password.startswith("$2b$"))


    def test_invalid_username_signup(self):
        """Signup with invalid username"""
        bad = User.signup(None, 'testagain@test.com', 'password', None)
        bad_id = 10000000
        bad.id = bad_id
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)
        

    
    def test_user_authentication(self):
        """Test user authentications works as intended with bcrypt pass hash"""
        
        good_auth = User.authenticate(self.username2, "HASHED_PASSWORD_TWO")
        bad_auth_pass = User.authenticate(self.username2, "NOTU2PASSWORD")
        bad_auth_username = User.authenticate('NONEEXISTENT USERNAME', "HASHED_PASSWORD_TWO")
        

        self.assertEqual(good_auth, self.u2)
        self.assertFalse(bad_auth_pass)
        self.assertFalse(bad_auth_username)



        





        


