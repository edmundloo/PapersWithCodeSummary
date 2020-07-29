from .cached_data import CachedData


class GitHubRepo:
    def __init__(self, url, gh_api):
        self.url = url
        self.repo_name = self._get_github_repo_name(self.url)
        self.gh_api = gh_api

        self.repo_cache = CachedData(self._get_repo)
        self.languages_cache = CachedData(self._get_languages)

    def search(self, query):
        """
        GitHub API, search for query within a repository.
        """
        return self.gh_api.search_code(query, repo=self.repo_name,)

    # Properties
    @property
    def repo(self, update_cache=False):
        if update_cache:
            self.repo_cache.update_data()
        return self.repo_cache.get_data()

    @property
    def languages(self, update_cache=False):
        if update_cache:
            self.languages_cache.update_data()
        return self.languages_cache.get_data()

    # Private functions
    def _get_repo(self):
        """
        GitHub API, get the SDK Repository object from GitHub.
        """
        gh_repo = self.gh_api.get_repo(self.repo_name)
        self.repo_name = gh_repo.full_name
        return gh_repo

    def _get_languages(self):
        """
        GitHub API, get languages for this repository.
        """
        return self.repo.get_languages()

    def _get_github_repo_name(self, github_repo_url):
        """
        Get the name of the GitHub repo from a GitHub repo URL.
        """
        url_parts = github_repo_url.split("/")
        base_url_index = url_parts.index("github.com")

        # Just a sanity check, this shouldn't be hit if all the URLs
        # are GitHub URLs
        assert base_url_index >= 0

        # Pull out the first two arguments after the base url,
        # this should represent GH username and repo
        return "/".join(url_parts[base_url_index + 1 : base_url_index + 3])
