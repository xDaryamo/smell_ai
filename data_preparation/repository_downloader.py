import os
import json
import logging
import shutil
from github import Github, GithubException
from dotenv import load_dotenv
from git import Repo
from concurrent.futures import ThreadPoolExecutor


class RepositoryDownloader:
    def __init__(
        self,
        token,
        output_folder="datasets/raw",
        libraries=["pandas", "numpy", "torch", "tensorflow", "sklearn"],
    ):
        """
        Initialize the downloader.

        :param token: GitHub token for authentication.
        :param output_folder: Folder to store the downloaded repositories.
        :param libraries: Optional list of target
        libraries to search for in dependency files.
        """
        self.github = Github(token)
        self.output_folder = output_folder
        self.libraries = libraries
        os.makedirs(self.output_folder, exist_ok=True)
        self.processed_repos = (
            set()
        )  # Tracks processed repositories to avoid duplicates
        self.processed_repos_path = os.path.join(
            os.path.dirname(__file__), "processed_repos.json"
        )
        self.load_processed_repos()

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("downloader.log"),
                logging.StreamHandler(),
            ],
        )

    def save_processed_repos(self):
        """Save the list of processed repositories to a JSON file."""
        with open(self.processed_repos_path, "w") as f:
            json.dump(list(self.processed_repos), f)

    def load_processed_repos(self):
        """Load the list of processed repositories from a JSON file."""
        if os.path.exists(self.processed_repos_path):
            with open(self.processed_repos_path, "r") as f:
                self.processed_repos = set(json.load(f))

    def search_and_process_topics(
        self,
        topics,
        max_repos_per_topic=10,
        stars=">=50",
        pushed=">2023-01-01",
        language="Python",
        download=False,
    ):
        """
        Search for repositories across multiple
        topics and either print or download them.

        :param topics: List of topics to search for.
        :param max_repos_per_topic: Maximum number of repositories per topic.
        :param stars: Filter repositories based on star count (e.g., '>=50').
        :param pushed: Filter repositories based on last update date
        (e.g., '>2023-01-01').
        :param language: Programming language to filter by (default: Python).
        :param download: If True, download repositories.
        If False, print repository information.
        """
        logging.info("Starting repository search for multiple topics...")
        for topic in topics:
            query = (
                f"language:{language} topic:{topic} "
                f"stars:{stars} pushed:{pushed}"
            )
            logging.info(
                f"Searching for topic: '{topic}' with query: '{query}'"
            )
            self._process_query(query, max_repos_per_topic, download)

        action = "downloaded" if download else "printed"
        logging.info(
            f"Repository processing completed! {len(self.processed_repos)} "
            f" unique repositories {action}."
        )
        self.save_processed_repos()

    def _process_query(self, query, max_repos, download):
        """
        Process a GitHub query and either print or download repositories.

        :param query: GitHub search query.
        :param max_repos: Maximum number of repositories to process.
        :param download: If True, download repositories.
        If False, print information.
        """
        repos = self.github.search_repositories(query=query)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for repo in repos[:max_repos]:
                futures.append(
                    executor.submit(self._process_repo, repo, download)
                )
            for future in futures:
                future.result()

    def _process_repo(self, repo, download):
        """
        Process a single repository.

        :param repo: GitHub repository object.
        :param download: If True, download the repository.
        If False, print information.
        """
        if repo.full_name in self.processed_repos:
            return

        if download:
            if self._download_repo(repo):
                self.processed_repos.add(repo.full_name)
        else:
            if self._print_repo_if_relevant(repo):
                self.processed_repos.add(repo.full_name)

    def _download_repo(self, repo):
        """
        Download a repository if it contains relevant libraries.

        :param repo: GitHub repository object.
        :return: True if the repository was downloaded, False otherwise.
        """
        repo_name = repo.full_name.replace("/", "_")
        repo_path = os.path.join(self.output_folder, repo_name)

        if os.path.exists(repo_path):
            logging.warning(
                f"Repository path {repo_path} already exists. "
                "Skipping download."
            )
            return False

        try:
            logging.info(f"Cloning {repo.full_name}...")
            Repo.clone_from(repo.clone_url, repo_path)
        except Exception as e:
            logging.error(f"Error cloning {repo.full_name}: {e}")
            return False

        if not self._contains_relevant_libraries(repo_path):
            logging.info(
                f"Repository {repo.full_name} discarded: "
                "no relevant libraries found."
            )
            shutil.rmtree(repo_path, ignore_errors=True)
            return False

        logging.info(f"Repository {repo.full_name} successfully downloaded.")
        return True

    def _print_repo_if_relevant(self, repo):
        """
        Print repository information if it contains relevant libraries.

        :param repo: GitHub repository object.
        :return: True if the repository is printed, False otherwise.
        """
        if self._contains_relevant_libraries_online(repo):
            logging.info(f"Repository: {repo.full_name}")
            logging.info(f"   Stars: {repo.stargazers_count}")
            logging.info(f"   Description: {repo.description}")
            logging.info(f"   Last Updated: {repo.updated_at}")
            logging.info(f"   URL: {repo.html_url}\n")
            return True
        return False

    def _contains_relevant_libraries_online(self, repo):
        """
        Check if a repository contains relevant
        libraries in dependency files online.

        :param repo: GitHub repository object.
        :return: True if at least one relevant\
         library is found, otherwise False.
        """
        files_to_check = ["requirements.txt", "setup.py", "pyproject.toml"]
        for file in files_to_check:
            try:
                content = repo.get_contents(file)
                decoded_content = content.decoded_content.decode(
                    "utf-8"
                ).lower()
                for lib in self.libraries:
                    if lib in decoded_content:
                        return True
            except GithubException:
                continue  # File not found or access denied
        return False

    def _contains_relevant_libraries(self, repo_path):
        """
        Check for relevant libraries in local dependency files.

        :param repo_path: Local path of the repository.
        :return: True if at least one
        relevant library is found, otherwise False.
        """
        files_to_check = ["requirements.txt", "setup.py", "pyproject.toml"]
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file in files_to_check:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read().lower()
                            for lib in self.libraries:
                                if lib in content:
                                    return True
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, "r", encoding="latin1") as f:
                                content = f.read().lower()
                                for lib in self.libraries:
                                    if lib in content:
                                        return True
                        except Exception as e:
                            logging.warning(
                                f"Skipping unreadable file: {file_path} ({e})"
                            )
        return False


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("GITHUB_TOKEN")

    downloader = RepositoryDownloader(token=TOKEN)

    topics = [
        "machine-learning",
        "deep-learning",
        "data-science",
        "pandas",
        "tensorflow",
        "sklearn",
        "torch",
        "transformers",
    ]
    downloader.search_and_process_topics(
        topics=topics,
        max_repos_per_topic=20,
        stars=">=100",
        pushed=">2023-06-01",
        language="Python",
        download=True,
    )
