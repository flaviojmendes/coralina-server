from datetime import datetime
from os import environ
from firebase_admin import firestore
from models.user_model import UserViewModel
from firebase_admin import credentials
from firebase_admin import initialize_app

db = firestore.client()


def get_user_stories(user_login: str):
    doc_ref = db.collection(u'stories').where(
        u'owner', u'==', user_login).get()
    stories = []
    for story in doc_ref:
        stories.append(story.to_dict())
    return stories