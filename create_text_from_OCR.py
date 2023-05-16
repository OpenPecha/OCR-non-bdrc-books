import os
import json
import gzip
import requests
from github import Github
from pathlib import Path

ACCESS_TOKEN = os.environ.get('GITHUB_TOKEN')

def add_description(repo_name, description):
    GITHUB_API_ENDPOINT = f"https://api.github.com/repos/MonlamAI/{repo_name}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {ACCESS_TOKEN}",
    }
    data = {
        "name": repo_name,
        "description": description,
    }
    
    response = requests.patch(GITHUB_API_ENDPOINT, json=data, headers=headers)
    response.raise_for_status()
    print("Description added successfully.")


def create_repo_and_upload_images(text, images_path, repo_name, title):
    g = Github(ACCESS_TOKEN)
    org = g.get_organization('MonlamAI')
    org.create_repo(repo_name)
    with open(f'{title}.txt', 'w') as file:
        file.write(text)
    repo = g.get_repo(f'MonlamAI/{repo_name}')
    repo.create_file(f'{title}.txt', 'Initial commit', text)
    add_description(repo_name, title)


def has_space_attached(symbol):
    if ('property' in symbol and 
            'detectedBreak' in symbol['property'] and 
            'type' in symbol['property']['detectedBreak'] and 
            symbol['property']['detectedBreak']['type'] == "SPACE"):
        return True
    return False

def get_bbox_text(response):
    text = ""
    for page in response['fullTextAnnotation']['pages']:
        for block in page['blocks']:
            for paragraph in block['paragraphs']:
                text += "\n"
                for word in paragraph['words']:
                    cur_word = ""
                    for symbol in word['symbols']:
                        cur_word += symbol['text']
                        if has_space_attached(symbol):
                            cur_word += " "
                    if cur_word:
                        text += cur_word
    return text


def get_text_from_OCR(OCR_path):
    final_text = ""
    file_paths = sorted(OCR_path.iterdir())
    for file_path in file_paths:
        ocr_object = json.load(gzip.open(str(file_path), "rb"))
        text = get_bbox_text(ocr_object)
        final_text += text
    return final_text

def create_repo_for_text(OCR_dir_path):
    OCR_paths = OCR_dir_path.iterdir()
    for num, OCR_path in enumerate(OCR_paths, 50):
        repo_name = f"MT_OCR{num:05}"
        title = OCR_path.stem
        text = get_text_from_OCR(OCR_path)
        create_repo_and_upload_images(text,Path(f"./data/images/{title}"), repo_name, title)


if __name__ == "__main__":
    OCR_dir_path= Path(f"./data/OCR/")
    create_repo_for_text(OCR_dir_path)