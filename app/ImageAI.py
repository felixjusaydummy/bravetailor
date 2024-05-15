
import requests
import json
import os

def getPrompt_from_GeminiAI(images):
    '''
    Accepts a list of images. Elements are in String format, base64
    '''

    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro-vision:generateContent"
    tkey = os.environ.get('APIKEY_GEMINI')
    key = f"key={tkey}"
    query = f"{url}?{key}"

    prompt = "combine to a new style from these images, do not include background"
    part_init = [{"text": prompt}]
    for i in images:
        tmp_i = {"inlineData": {"mimeType": "image/png", "data": i }}
        part_init.append(tmp_i)

    data = {"contents": [{"parts": part_init}]}

    response = requests.post(query, headers={}, json=data)

    if response.status_code == 200:
        # print("Response from Gemini:", response.json())
        # print('\n')
        # print(response.json()['choices'][0]['message']['content'])

        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
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

