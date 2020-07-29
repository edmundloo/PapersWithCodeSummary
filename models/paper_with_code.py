from .github_repo import GitHubRepo


class PaperWithCode:
    def __init__(self, paper_with_code_info, gh_api):
        self.paper_url = paper_with_code_info["paper_url_abs"]
        self.github_repo = GitHubRepo(paper_with_code_info["repo_url"], gh_api)
        self.proceeding = paper_with_code_info["proceeding"]

        if "plugin_output" in paper_with_code_info:
            self.plugin_output = paper_with_code_info["plugin_output"]
        else:
            self.plugin_output = []

    def apply_plugins(self, plugins):
        """
        Takes in a list of PaperWithCodePlugin classes and runs each plugin,
        adding the plugin_key to the plugin_output list.
        """
        for plugin in plugins:
            initialized_plugin = plugin(self)
            if initialized_plugin.apply():
                self.plugin_output.append(initialized_plugin.key)

    def serialize(self):
        """
        We can only store serializable formats in pickleDB, so we need this.
        """
        return {
            "paper_url_abs": self.paper_url,
            "repo_url": self.repo.url,
            "plugin_output": self.plugin_output,
            "proceeding": self.proceeding if self.proceeding != None else "",
        }

    @property
    def url(self):
        return self.paper_url

    @property
    def repo(self):
        return self.github_repo

    @property
    def ml_tools(self):
        return self.plugin_output
