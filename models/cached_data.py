class CachedData:
    """
    Basic structure used to reduce calling the "fetch_fn",
    this if often an API call.
    """

    def __init__(self, fetch_fn):
        self.fetch_fn = fetch_fn
        self.cached_data = None
        self.cache_populated = False

    def update_data(self):
        self.cached_data = self.fetch_fn()
        self.cache_populated = True

    def get_data(self):
        # Only populate data if there is no previous value
        if self.cache_populated == False:
            self.update_data()
        return self.cached_data
