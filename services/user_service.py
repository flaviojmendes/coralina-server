from datetime import datetime
from os import environ
import os
from firebase_admin import firestore
from models.user_model import UserViewModel
from firebase_admin import credentials
from firebase_admin import initialize_app


cred = credentials.Certificate("auth.json")
initialize_app(cred)

# cred = credentials.ApplicationDefault()
# initialize_app(cred, {
#     'projectId': "coralina",
# })

db = firestore.client()


def create_user(user: UserViewModel):
    doc_ref = db.collection(u'users').document(user.user_login)
    if doc_ref.get().exists:
        return False

    doc_ref.set({
        u'user_login': user.user_login,
        u'creation': datetime.now(),
        u'last_login': datetime.now(),
        u'tokens': 2
    })

    return True


def update_user(user: UserViewModel):
    doc_ref = db.collection(u'users').document(user.user_login)
    if doc_ref.get().exists:
        doc_ref.set({
            u'last_login': datetime.now()
        })

    return True


def decrement_user_token(user_login: str):
    doc_ref = db.collection(u'users').document(user_login)
    if doc_ref.get().exists:
        user_dict = doc_ref.get().to_dict()
        current_tokens = user_dict['tokens'] - 1
        doc_ref.set({u'user_login': user_login,
                    u'tokens': current_tokens
                     })


def process_sale(user_login: str, product_id: str, tokens: int):

    if product_id == os.getenv("GUMROAD_PRODUCT_ID"):
        doc_ref = db.collection(u'users').document(user_login)
        if doc_ref.get().exists:
            user_dict = doc_ref.get().to_dict()
            current_tokens = user_dict['tokens'] + (tokens * 5)
            doc_ref.set({u'user_login': user_login,
                        u'tokens': current_tokens
                        })


def get_user(user_login: str):
    doc_ref = db.collection(u'users').document(user_login)
    if doc_ref.get().exists:
        return doc_ref.get().to_dict()
    raise Exception("User does not exist")
