"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from cgitb import text
import os
from unittest import TestCase

from models import db, connect_db, Message, User
from sqlalchemy import exc
from sqlalchemy.orm.exc import NoResultFound

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
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            html = resp.get_data(as_text=True)
            
            self.assertIn('Redirecting', html)
            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            self.assertEqual(msg.user_id, sess[CURR_USER_KEY])

    def test_view_message(self):
        """can we view a message. is follow/unfollow displayed when logged-in?"""
        user = User.signup(username='fakeuser', email='fake@fake.com', password='password', image_url=None)
        userid = 80085
        user.id = userid
        db.session.commit()

        msg = Message(text='fake users message', user_id=userid)
        msgid = 800855
        msg.id = msgid
        user.messages.append(msg)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            


            resp = c.get(f'/messages/{msgid}')

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn('fakeuser', html)
            self.assertIn('Follow', html)

    
    def test_view_invalid_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/messages/wow')

            self.assertEqual(resp.status_code, 404)         


    def test_delete_message(self):
        """Deleting our own added msg"""

        msg1 = Message(text='Our Users MSG', user_id=self.testuser.id)
        msgid=12345
        msg1.id = msgid
        self.testuser.messages.append(msg1)
        db.session.commit() 

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = Message.query.get(msgid)    

            resp = c.post(f'/messages/{msg.id}/delete',  follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn(f'{self.testuser.username}', html)
            self.assertIn('Edit Profile', html)
            self.assertIn('Delete Profile', html)
            
            
            self.assertIsNone(Message.query.get(msg.id))

    def test_add_message_logged_out(self):
        """When you’re logged out, are you prohibited from adding messages?"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            
            self.assertIn("Access unauthorized.", html)

            
            self.assertIsNone(Message.query.first())
            self.assertEqual(len(Message.query.all()), 0)

    
    def test_delete_message_logged_out(self):
        """When you’re logged out, are you prohibited from deleting messages?"""

        msg1 = Message(text='Our Users MSG', user_id=self.testuser.id)
        msgid=12345
        msg1.id = msgid
        self.testuser.messages.append(msg1)
        db.session.commit()
        
        with self.client as c:
            resp = c.post(f'/messages/{msgid}/delete',  follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Access unauthorized.", html)

            self.assertIsNotNone(Message.query.get(msgid))
            self.assertEqual(len(Message.query.all()), 1)
        
        
    
    def test_delete_message_prohibited(self):
        """When you’re logged in, are you prohibiting from adding a message as another user"""

        user = User.signup(username='fakeuser', email='fake@fake.com', password='password', image_url=None)
        userid = 80085
        user.id = userid
        db.session.commit()

        msg = Message(text='fake users message', user_id=userid)
        msgid = 800855
        msg.id = msgid
        user.messages.append(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = Message.query.get(msgid)    

            resp = c.post(f'/messages/{msgid}/delete',  follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Access unauthorized.", html)
            self.assertIsNotNone(Message.query.get(msgid))
            self.assertEqual(len(Message.query.all()), 1)

               







           
            
            

            




