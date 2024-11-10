from flask import Blueprint, request, jsonify, send_file
import openai
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os
import json

load_dotenv()  # This reads the .env file

api_key = os.getenv("API_KEY")
openai.api_key = str(api_key)

chatOutput = Blueprint('chatOutput', __name__)

# @chatOutput.route('/chatOutput', methods=['POST'])
def get_image_description(image_url):
   inputPrompt = """
   Given an image, first determine if the item shown can be recycled, reused, salvaged, or useless. Choose one and explain how it can be used in this way. If it is useless, then it is safe to go in the landfill. Provide detailed instructions and educational notes about the item, including its proper disposal method if applicable. 
   Specify if you are not able to view the image if it is unclear or due to security or can't access. 
   You are able to access certains links but not others explain that. 

   This is the format the response as a JSON. DO NOT PUT ```json ``` ANYWHERE IN IT:

    {
      "Item Name": "Put Name Here",
      "Use": "Recycle, reuse, salvage, useless",
      "Information on Use": "Details here",
      "Educational Facts": "Facts here",
    }
   
   Do not include unnecessary words, only use the format given. Do not use special characters for organization."""

   response = openai.chat.completions.create(
      model="gpt-4-turbo",  # Use the correct model name
      messages=[
         {
               "role": "user",
               "content": [
                  {"type": "text", "text": inputPrompt},
                  {
                     "type": "image_url",
                     "image_url": {
                        "url": image_url,
                     },
                  },
               ],
               "response_format": {
                  "type": "json_object"
               },
               "temperature": 0.2
         }
      ],
      max_tokens=300,
   )

   response_content = response.choices[0].message.content
   data = json.loads(response_content)
   data["url"] = image_url

   return data

def chat_output_route(url):
   json_response = get_image_description(url)
   return json_response


    




