class BasePaperWithCodePlugin:
    def __init__(self, pwc):
        self.pwc = pwc

        # plugin_key should always be set in plugins since this is what
        # identifies the tool that met the heuristic in the output
        self.plugin_key = None

    def apply(self):
        """
        Heuristics for the tool you're trying to detect should go here,
        returning True if the condition is met and False if not.
        """
        raise NotImplementedError(
            "BasePaperWithCodePlugin 'apply' method not implemented."
        )

    @property
    def key(self):
        return self.plugin_key


# All plugins below should be based on BasePaperWithCodePlugin
class MatlabPlugin(BasePaperWithCodePlugin):
    def apply(self):
        self.plugin_key = "matlab"

        gh = self.pwc.github_repo
        if any(["matlab" == language.lower() for language in gh.languages]):
            return True
        return False


class NumpyPlugin(BasePaperWithCodePlugin):
    def apply(self):
        self.plugin_key = "numpy"

        gh = self.pwc.github_repo
        if gh.search("numpy").totalCount > 0:
            return True
        return False


class ScikitPlugin(BasePaperWithCodePlugin):
    def apply(self):
        self.plugin_key = "scikit"

        gh = self.pwc.github_repo
        if gh.search("scipy").totalCount > 0 or gh.search("sklearn").totalCount > 0:
            return True
        return False


class TensorflowPlugin(BasePaperWithCodePlugin):
    def apply(self):
        self.plugin_key = "tensorflow"

        gh = self.pwc.github_repo
        if gh.search("tensorflow").totalCount > 0:
            return True
        return False


class PytorchPlugin(BasePaperWithCodePlugin):
    def apply(self):
        self.plugin_key = "pytorch"

        gh = self.pwc.github_repo
        if gh.search("pytorch").totalCount > 0:
            return True
        return False


ALL_PLUGINS = [
    MatlabPlugin,
    NumpyPlugin,
    ScikitPlugin,
    TensorflowPlugin,
    PytorchPlugin,
]
