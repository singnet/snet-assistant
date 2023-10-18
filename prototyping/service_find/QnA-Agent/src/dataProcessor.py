import concurrent.futures
import io
import json
import os
import pathlib
import pandas as pd
import re
import requests
import tiktoken
import zipfile
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from markdown import markdown
from pathlib import Path
import markdown

ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo")

CHUNK_SIZE = 200  # The target size of each text chunk in tokens
MIN_CHUNK_SIZE_CHARS = 350  # The minimum size of each text chunk in characters
MIN_CHUNK_LENGTH_TO_EMBED = 5  # Discard chunks shorter than this
MAX_NUM_CHUNKS = 300  # The maximum number of chunks to generate from a text
ENDPAGE_NUM = 282  # the last page number


def download_files(url: str, local_directory: str) -> None:
    """Downloads the ZIP archive at the given URL to the local directory.

    Args:
        url: The URL of the ZIP archive.
        local_directory: The directory to store the downloaded files.
    """

    # Make a request to download the ZIP archive.
    response = requests.get(url)

    # Check if the request was successful (status code 200).
    if response.status_code != 200:
        raise RuntimeError(
            f"Error: Unable to fetch repository. Status code {response.status_code}")

    # Create a directory to store the downloaded files.
    os.makedirs(f"{local_directory}/new_data", exist_ok=True)

    # Extract the ZIP archive.
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(f"{local_directory}/new_data")

    print(f"Repository downloaded to {local_directory}")


def get_all_links(data_url: str) -> list[str]:
    """Returns a list of all the markdown links in the given directory."""

    try:
        return glob(f"{data_url}/**/*.md", recursive=True)
    except Exception as e:
        print(e)
        return []


def save_data(link: str) -> str:
    """Saves the contents of the given markdown file to a string."""

    pattern_to_remove = r'Page settings.*?\nMicro navigation\n.*?(?=\n\n|\Z)'

    text = ""
    with open(link, "r", encoding="utf-8") as input_file:
        text = input_file.read()

    html = markdown.markdown(text)
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text()
    clean_text = re.sub(pattern_to_remove, "\n", text,
                        flags=re.DOTALL | re.IGNORECASE)

    return clean_text


def get_md_files_in_all_directories(lo_url: str) -> dict[str, list[str]]:
    """Returns a dictionary of all the markdown files in the given directory and its subdirectories."""

    total = {}
    for dirpath, _, _ in os.walk(lo_url):
        l = []
        temp = []
        if dirpath != lo_url:
            l = get_all_links(dirpath)
            with ThreadPoolExecutor(max_workers=5) as executor:
                results = executor.map(save_data, l)

            for result in results:
                temp.append(result)

            total[dirpath] = temp

    return total, l
