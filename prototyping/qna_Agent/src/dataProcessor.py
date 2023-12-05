import os
import io
import re
import shutil
import zipfile
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from pathlib import Path
import markdown
import tiktoken


ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo")
CHUNK_SIZE = 200  # The target size of each text chunk in tokens
MIN_CHUNK_SIZE_CHARS = 350  # The minimum size of each text chunk in characters
MIN_CHUNK_LENGTH_TO_EMBED = 5  # Discard chunks shorter than this
MAX_NUM_CHUNKS = 300  # The maximum number of chunks to generate from a text
ENDPAGE_NUM = 282  # the last page number


class DataProcessor:

    def __init__(self, repo_url):
        """Initialize DataProcessor.

        Args:
            repo_url (str): URL of the ZIP archive.
        """
        self.repo_url = repo_url
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__)))
        self.data_dir_path = os.path.join(self.base_dir, "data")
        self.docs_path = [os.path.join(self.data_dir_path, "dev-portal-master/docs"), os.path.join(self.data_dir_path, "dev-portal-master/tutorials")]
        self.total = {}
        self.download_files()
        self.get_md_files_in_all_directories()
        self.save_to_csv()
        self.delete_dir()

    def download_files(self) -> None:
        """Downloads the ZIP archive at the given URL to the local directory."""

        # Make a request to download the ZIP archive.
        response = requests.get(self.repo_url)

        # Check if the request was successful (status code 200).
        if response.status_code != 200:
            raise RuntimeError(
                f"Error: Unable to fetch repository. Status code {response.status_code}")

        # Create a directory to store the downloaded files.
        os.makedirs(self.data_dir_path, exist_ok=True)

        # Extract the ZIP archive.
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(f"{self.data_dir_path}")

        print(f"Repository downloaded to {self.data_dir_path}")

    @staticmethod
    def get_all_links(data_url: str, level=2) -> list[str]:
        """Returns a list of all the markdown links in the given directory.

        Args:
            data_url (str): Directory path containing markdown files.

        Returns:
            list: List of markdown file paths.
        """

        try:
            result = glob(f"{data_url}/*.md", recursive=True)
            if level == 2:
                result.extend(glob(f"{data_url}/*/*.md", recursive=True))
            return result
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def save_data(link: str) -> str:
        """Saves the contents of the given markdown file to a string.

        Args:
            link (str): Path to the markdown file.

        Returns:
            str: Cleaned markdown content.
        """
        with open(link, "r", encoding="utf-8") as input_file:
            text = input_file.read()

        html = markdown.markdown(text)
        soup = BeautifulSoup(html, "html.parser")

        text = soup.get_text().strip()
        if text.startswith("Page settings") and "\n\n" in text:
            text = text[str(text).find("\n\n") + 2:]
        return text

    @staticmethod
    def get_top_level_dirs(dir_path):
        """Returns a list of the full paths of all the top-level directories in the specified directory.

        Args:
            dir_path (str): Directory path.

        Returns:
            list: List of top-level directory paths.
        """
        dir_path = Path(dir_path)
        top_level_dirs = [x for x in dir_path.iterdir() if x.is_dir()]
        return list(top_level_dirs)

    def get_md_files_in_all_directories(self) -> dict[str, list[str]]:
        """Returns a dictionary of all the markdown files in the given directory and its subdirectories."""
        list_dirs = []
        for ph in self.docs_path:
            list_dirs.extend(self.get_top_level_dirs(ph))
        list_dirs.extend(self.docs_path)
        for dirpath in list_dirs:
            temp = []
            if dirpath not in self.docs_path:
                l = self.get_all_links(dirpath)
            else:
                l = self.get_all_links(dirpath, level=1)
            with ThreadPoolExecutor(max_workers=5) as executor:
                results = executor.map(self.save_data, l)

            for result in results:
                temp.append(result)

            self.total[dirpath] = temp

    @staticmethod
    def get_text_chunks(text: str, chunk_token_size: int = CHUNK_SIZE) -> list[str]:
        """Splits a text into chunks of ~CHUNK_SIZE tokens, based on punctuation and newline boundaries.

        Args:
            text (str): Text content to split into chunks.
            chunk_token_size (int, optional): The target size of each chunk in tokens. Defaults to CHUNK_SIZE.

        Returns:
            list: List of text chunks.
        """
        tokens = ENCODING.encode(text)

        chunks = []
        chunk_size = chunk_token_size
        num_chunks = 0

        while tokens:
            chunk = tokens[:chunk_size]

            chunk_text = ENCODING.decode(chunk)

            if not chunk_text or chunk_text.isspace():
                tokens = tokens[len(chunk):]
                continue

            last_punctuation = max(chunk_text.rfind(
                "."), chunk_text.rfind("\n"), chunk_text.rfind("\n\n"))

            if last_punctuation != -1 and last_punctuation > MIN_CHUNK_SIZE_CHARS:
                chunk_text = chunk_text[: last_punctuation + 1]

            chunk_text_to_append = chunk_text.replace("\n", " ").strip()

            if len(chunk_text_to_append) > MIN_CHUNK_LENGTH_TO_EMBED:
                chunks.append(chunk_text_to_append)

            tokens = tokens[len(ENCODING.encode(chunk_text)):]
            num_chunks += 1

        if tokens:
            remaining_text = ENCODING.decode(tokens).replace("\n", " ").strip()
            if len(remaining_text) > MIN_CHUNK_LENGTH_TO_EMBED:
                chunks.append(remaining_text)

        return chunks

    def save_to_csv(self):
        """Saves the processed data to a CSV file."""
        total_test = []

        for key, value in (self.total.items()):
            temp1 = []
            if len(value) > 0:
                for i in value:
                    temp1.append(self.get_text_chunks(i))
                    paths = Path(key)
                    paths = "/".join(paths.parts[-2:])
                total_test.append([paths, temp1])
        df_temp = pd.DataFrame(total_test, columns=['path', 'chuck_text'])
        df_temp.to_csv(os.path.join(
            self.data_dir_path, "dataset.csv"), index=False)

    def delete_dir(self):
        """Deletes the 'dev-portal-master' directory."""
        shutil.rmtree(os.path.join(self.data_dir_path, "dev-portal-master"))
