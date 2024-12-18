import os
from github import Github, GithubException
from dotenv import load_dotenv


class RepositoryDownloader:
    def __init__(
        self,
        token,
        output_folder="datasets/raw",
        libraries=[
            "pandas",
            "numpy",
            "torch",
            "tensorflow",
            "sklearn",
        ],
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
        )  # Tracks processed repositories to avoid duplicates.

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
        Search for repositories across multiple topics and either
        print or download them.

        :param topics: List of topics to search for.
        :param max_repos_per_topic: Maximum number of repositories per topic.
        :param stars: Filter repositories based on star count (e.g., '>=50').
        :param pushed: Filter repositories based on last update date
         (e.g., '>2023-01-01').
        :param language: Programming language to filter by (default: Python).
        :param download: If True, download repositories.
         If False, print repository information.
        """
        print("Starting repository search for multiple topics...\n")
        for topic in topics:
            query = f"language:{language} topic:{topic}"
            f"stars:{stars} pushed:{pushed}"
            print(f"Searching for topic: '{topic}' with query: '{query}'")
            self._process_query(query, max_repos_per_topic, download)

        action = "downloaded" if download else "printed"
        print(
            f"Repository processing completed! {len(self.processed_repos)} "
            f"unique repositories {action}."
        )

    def _process_query(self, query, max_repos, download):
        """
        Process a GitHub query and either print or download repositories.

        :param query: GitHub search query.
        :param max_repos: Maximum number of repositories to process.
        :param download: If True, download repositories.
          If False, print information.
        """
        repos = self.github.search_repositories(query=query)
        count = 0

        for repo in repos:
            if count >= max_repos:
                break

            if repo.full_name in self.processed_repos:
                continue  # Skip already processed repositories

            if download:
                if self._download_repo(repo):
                    count += 1
            else:
                if self._print_repo_if_relevant(repo):
                    count += 1

            self.processed_repos.add(repo.full_name)

    def _download_repo(self, repo):
        """
        Download a repository if it contains relevant libraries.

        :param repo: GitHub repository object.
        :return: True if the repository was downloaded, False otherwise.
        """
        repo_name = repo.full_name.replace("/", "_")
        repo_path = os.path.join(self.output_folder, repo_name)

        print(f"Cloning {repo.full_name}...")
        os.system(f"git clone {repo.clone_url} {repo_path}")

        if not self._contains_relevant_libraries(repo_path):
            print(
                f"Repository {repo.full_name} discarded: "
                "no relevant libraries found."
            )
            os.system(f"rm -rf {repo_path}")
            return False

        print(f"Repository {repo.full_name} successfully downloaded.")
        return True

    def _print_repo_if_relevant(self, repo):
        """
        Print repository information if it contains relevant libraries.

        :param repo: GitHub repository object.
        :return: True if the repository is printed, False otherwise.
        """
        if self._contains_relevant_libraries_online(repo):
            print(f"Repository: {repo.full_name}")
            print(f"   Stars: {repo.stargazers_count}")
            print(f"   Description: {repo.description}")
            print(f"   Last Updated: {repo.updated_at}")
            print(f"   URL: {repo.html_url}\n")
            return True
        return False

    def _contains_relevant_libraries_online(self, repo):
        """
        Check if a repository contains relevant
        libraries in dependency files online.

        :param repo: GitHub repository object.
        :return: True if at least one relevant
         library is found, otherwise False.
        """
        files_to_check = ["requirements.txt", "setup.py", "pyproject.toml"]
        for file in files_to_check:
            try:
                content = repo.get_contents(file)
                decoded_content = content.decoded_content.decode(
                    "utf-8"
                ).lower()
                if any(lib in decoded_content for lib in self.libraries):
                    return True
            except GithubException:
                continue  # File not found or access denied
        return False

    def _contains_relevant_libraries(self, repo_path):
        """
        Check for relevant libraries in local dependency files.

        :param repo_path: Local path of the repository.
        :return: True if at least one relevant
         library is found, otherwise False.
        """
        files_to_check = ["requirements.txt", "setup.py", "pyproject.toml"]
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file in files_to_check:
                    file_path = os.path.join(root, file)
                    try:
                        # Try reading the file with UTF-8
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read().lower()
                            if any(lib in content for lib in self.libraries):
                                return True
                    except UnicodeDecodeError:
                        # Handle non-UTF-8 files gracefully
                        try:
                            with open(file_path, "r", encoding="latin1") as f:
                                content = f.read().lower()
                                if any(
                                    lib in content for lib in self.libraries
                                ):
                                    return True
                        except Exception as e:
                            print(
                                f"Skipping unreadable file: {file_path} ({e})"
                            )
        return False


# TEST

if __name__ == "__main__":

    load_dotenv()
    TOKEN = os.getenv("GITHUB_TOKEN")

    downloader = RepositoryDownloader(token=TOKEN)

    # Define search parameters
    topics = [
        "machine-learning",
        "deep-learning",
        "data-science",
        "pandas",
        "tensorflow",
    ]
    stars = ">=100"
    pushed = ">2023-06-01"
    language = "Python"

    # Print repositories without downloading
    print("Printing repositories...\n")
    downloader.search_and_process_topics(
        topics=topics,
        max_repos_per_topic=5,
        stars=stars,
        pushed=pushed,
        language=language,
        download=True,
    )
