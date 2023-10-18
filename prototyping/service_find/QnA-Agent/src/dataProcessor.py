import io
import os
from concurrent.futures import ThreadPoolExecutor
from glob import glob
import re
import requests
from pathlib import Path
import zipfile
from bs4 import BeautifulSoup
import markdown
import pandas as pd
import json
import tiktoken


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
