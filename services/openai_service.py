import os
import openai

from models.plot_model import PlotModel
from models.story_model import ParagraphModel, StoryModel


async def generate_story(plot: PlotModel):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    plot_text = f'Write a {plot.theme} story in Brazilian Portuguese with the following characters and details:\n Main character: {plot.main_character} \n Secondary Characters: {plot.supporting_characters}\n Villain: {plot.villain}\n Please provide between 12 and 15 paragraphs, no longer than 2 lines each one. Do not enumerate them'
    # plot_text = f'Escreva uma história infantil com os seguintes personagens e detalhes:\n Protagonista: {plot.main_character} \n Coadjuvantes: {plot.supporting_characters}\n Vilão: {plot.villain}\n Detalhes: {plot.details}\n  Por favor forneça de 12 a 15 parágrafos, não maior do que 2 linhas cada um. Não enumere-os.'
    completion_resp = openai.Completion.create(prompt=plot_text, engine="text-davinci-003", max_tokens=1000)

    paragraphs_text = completion_resp['choices'][0]['text'].split("\n")
    paragraphs_text = list(filter(lambda text: len(text) > 10, paragraphs_text))
    paragraphs_text = group_paragraphs(paragraphs_text, 2)
    paragraphs = []
    for paragraph_text in paragraphs_text:
        paragraph = ParagraphModel(text=paragraph_text)
        generate_image(paragraph, plot)
        paragraphs.append(paragraph)


    story = StoryModel()
    story.paragraphs = paragraphs
    return story


def group_paragraphs(l, n):
    for i in range(0, len(l), n):
        yield " ".join(l[i:i + n])

def generate_image(paragraph: ParagraphModel, plot: PlotModel):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    image_resp = openai.Image.create(prompt=f"generate a prompt for dall-e to represent this scene with a {plot.theme} illustration: {paragraph.text} \n Having this context in mind:  {plot.main_character} \n {plot.supporting_characters}", n=1, size="512x512")
    paragraph.image_url = image_resp['data'][0]['url']


