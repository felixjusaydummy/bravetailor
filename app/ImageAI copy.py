
import requests
import json
import os

def getPrompt_init():
    
    # prompt 1
    # return "combine to a new style from these images, do not include background"

    # prompt 2
    stylelen = 3
    text1 =  f"You're an AI fashion designer who specializes in creating unique clothing designs using the latest AI design technology. Your task is to utilize the DALL-E Super Describe Model to generate at least {stylelen} different styles of clothing by deriving inspiration from the fabric in the images provided. Imagine each fabric as a source of creative inspiration, guiding you to craft distinct and appealing clothing designs. Ensure that each design reflects the essence of the fabric pattern, texture, and color scheme while incorporating innovative elements to make them stand out. For example, when presented with a floral-patterned fabric, you would envision a flowing summer dress with delicate petal-inspired embellishments. Similarly, a geometric-patterned fabric might inspire you to design a sleek and modern tailored suit with bold, structured lines. Remember to infuse your designs with creativity, incorporating a variety of silhouettes, styles, and details to showcase your AI fashion design expertise. Aim to create a diverse range of clothing styles that are both visually captivating and fashion-forward based on the fabric images provided."

    text2 = "output it in json format"
    return f'{text1}\n{text2}'

def getPrompt_from_GeminiAI(images):
    '''
    Accepts a list of images. Elements are in String format, base64
    '''

    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro-vision:generateContent"
    tkey = os.environ.get('APIKEY_GEMINI')
    key = f"key={tkey}"
    query = f"{url}?{key}"
    prompt = getPrompt_init()

    part_init = [{"text": prompt}]
    for i in images:
        tmp_i = {"inlineData": {"mimeType": "image/png", "data": i }}
        part_init.append(tmp_i)

    data = {"contents": [{"parts": part_init}]}

    response = requests.post(query, headers={}, json=data)

    if response.status_code == 200:

        final_prompt = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"final prompt: {final_prompt}")
        return final_prompt
    else:
        print("Error:", response.status_code, response.text)
        response.raise_for_status()



def getImage_from_openai(prompt):
    '''
    Accepts prompt text that came from "getPrompt_from_GeminiAI" function
    '''

    openai_api_key = os.environ.get('APIKEY_OPENAI')
    if openai_api_key is None:
        raise ValueError("OpenAI API key is not set in environment variables.")

    url = "https://api.openai.com/v1/images/generations"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    data = { "prompt": prompt }
    response = requests.post(url, headers=headers, json=data)
    print("code: {}".format(response.status_code))

    # Check if the request was successful
    if response.status_code == 200:
        print("Response from OpenAI:", response.json())
        print('\n')
        # print(response.json())
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        response.raise_for_status()



def createImage(images):
    '''
    Main function to be called from RestAPI
    '''
    prompt = getPrompt_from_GeminiAI(images)
    return getImage_from_openai(prompt)

