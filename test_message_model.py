

import os
from unittest import TestCase
from sqlalchemy import exc


from models import db, User, Message, Likes

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

class MessageModelTestCase(TestCase):
    """Test model for messages"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        
        self.uid = 88888
        u = User.signup('testuserone','messagetest@message.com','HASH_THIS_PASS', None)
        
        
        u.id = self.uid
        
        
        db.session.commit()
        self.user = User.query.get(self.uid)
        
        

        self.client = app.test_client()

    def tearDown(self):
        """Clear any fouled transactions"""
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """test basic message model"""
        msgid = 12345
        msg = Message(text='Test message', user_id=self.uid)
        msg.id = msgid
        db.session.add(msg)
        db.session.commit()
        
        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(msg.user, self.user)
        self.assertEqual(msg.text, 'Test message')
        self.assertEqual(msg.user.likes, [])

    def test_message_likes(self):
        """test when message gets likes w Likes model"""
        msg1 = Message(text='The second msg', user_id=self.uid) 
        msg2 = Message(text='Even more messages', user_id=self.uid)
        msg1id = 123456
        msg2id = 1234567
        msg1.id = msg1id
        msg2.id = msg2id
        db.session.add_all([msg1,msg2])
        db.session.commit()
        
        self.user.likes.append(msg1)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 2)
        self.assertEqual(msg1.id, 123456)
        self.assertEqual(msg2.id, 1234567)
        self.assertEqual(len(self.user.likes), 1)
        
        self.user.likes.append(msg2)
        db.session.commit()
        
        
        query = Likes.query.filter(Likes.user_id == self.uid).all()
        self.assertEqual(len(query), 2)
        self.assertEqual(query[0].message_id, msg1.id)
        self.assertEqual(query[1].user_id, self.user.id)
        

        self.user.likes = []
        db.session.commit()
        self.assertEqual(len(self.user.likes), 0)



        

        