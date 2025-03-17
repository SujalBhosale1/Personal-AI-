import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")

    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)

        except IOError as e:
            print(f"Unable to open {image_path}. Error: {e}")

API_URL = "https://api-inference.huggingface.co/models/stablilityai/stable-diffusion-xl-prompt-image-generation"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred during API request: {e}")
        return None

async def generate_images(prompt: str):
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }

        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            try:
                with open(fr"Data\{prompt.replace(' ','_')}{i+1}.jpg", "wb") as f:
                    f.write(image_bytes)
            except Exception as e:
                print(f"Error saving image {i+1}: {e}")

def GenerateImages(prompt: str):
    try:
        asyncio.run(generate_images(prompt))
        open_images(prompt)
    except Exception as e:
        print(f"Error during image generation: {e}")

while True:
    try:
        with open(r"frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()
        
        Prompt, Status = Data.split(",")
        
        if Status == "True":
            print("Generating Images...")
            GenerateImages(prompt=Prompt)

            with open(r"frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False, False")
                break

        else:
            sleep(1)

    except FileNotFoundError as e:
        print(f"Error: ImageGeneration.data file not found: {e}")
        sleep(5)  # Retry after some time if the file is missing

    except ValueError as e:
        print(f"Error: Failed to unpack data from file. Error: {e}")
        sleep(5)  # Retry after some time

    except Exception as e:
        print(f"Unexpected error: {e}")
        sleep(5)  # Retry after some time
