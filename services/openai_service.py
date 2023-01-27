import base64
from datetime import datetime
import uuid
from google.cloud import storage
import os
import openai
import requests
from exceptions.OutOfTokensException import OutOfTokensException

from models.plot_model import PlotModel
from models.story_model import ParagraphModel, StoryModel
from services.user_service import decrement_user_token, get_user
from firebase_admin import firestore
from models.user_model import UserViewModel
from firebase_admin import credentials
from firebase_admin import initialize_app


async def generate_story(plot: PlotModel, nickname: str):

    user = get_user(nickname)

    if (user['tokens'] > 0):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        plot_text = f'Write a {plot.theme} story in Brazilian Portuguese with the following characters and details:\n Main character: {plot.main_character} \n Secondary Characters: {plot.supporting_characters}\n Villain: {plot.villain}\n Please provide between 12 and 15 paragraphs, no longer than 2 lines each one. Do not enumerate them'
        # plot_text = f'Escreva uma história infantil com os seguintes personagens e detalhes:\n Protagonista: {plot.main_character} \n Coadjuvantes: {plot.supporting_characters}\n Vilão: {plot.villain}\n Detalhes: {plot.details}\n  Por favor forneça de 12 a 15 parágrafos, não maior do que 2 linhas cada um. Não enumere-os.'
        completion_resp = openai.Completion.create(
            prompt=plot_text, engine="text-davinci-003", max_tokens=1000)

        paragraphs_text = completion_resp['choices'][0]['text'].split("\n")
        paragraphs_text = list(
            filter(lambda text: len(text) > 10, paragraphs_text))
        paragraphs_text = group_paragraphs(paragraphs_text, 2)
        paragraphs = []
        for paragraph_text in paragraphs_text:
            paragraph = ParagraphModel(text=paragraph_text)
            generate_image(paragraph, plot)
            paragraphs.append(paragraph)

        story = StoryModel()
        story.paragraphs = paragraphs
        story.owner = nickname

        save_story(story)

        return story
    else:
        raise OutOfTokensException


def group_paragraphs(l, n):
    for i in range(0, len(l), n):
        yield " ".join(l[i:i + n])


def generate_image(paragraph: ParagraphModel, plot: PlotModel):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    image_resp = openai.Image.create(
        prompt=f"generate a prompt for dall-e to represent this scene with a {plot.theme} illustration: {paragraph.text} \n Having this context in mind:  {plot.main_character} \n {plot.supporting_characters}", n=1, size="512x512")
    paragraph.image_url = image_resp['data'][0]['url']

    response = requests.get(image_resp['data'][0]['url'])


    # Create a Google Cloud Storage client
    cred = credentials.Certificate("auth.json")

    client = storage.Client()

    # Get the bucket where you want to upload the image
    bucket = client.bucket("coralina")

    # Create a new blob in the bucket
    img_id = str(uuid.uuid4())
    blob = bucket.blob(img_id)

    # Upload the image data to the blob
    blob.upload_from_string(response.content, content_type='image/jpeg')
    
    paragraph.image_url = f'https://storage.cloud.google.com/coralina/{img_id}'

    # # check if the request was successful
    # if response.status_code == 200:
    #     # get the binary data of the image
    #     image_data = response.content
    #     # encode the binary data to a base64 string
    #     base64_image = base64.b64encode(image_data).decode()
    #     # print the base64 string
    #     paragraph.image_url = base64_image


def save_story(story: StoryModel):
    
    paragraphs_list = []
    for paragraph in story.paragraphs:
        paragraphs_list.append(paragraph.dict())
    
    
    db = firestore.client()

    doc_ref = db.collection(u'stories').document(str(uuid.uuid4()))
    
    doc_ref.set({
        u'owner': story.owner,
        u'paragraphs': paragraphs_list,
    })

    decrement_user_token(story.owner)
