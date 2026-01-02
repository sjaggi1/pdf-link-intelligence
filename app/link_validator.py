import requests

class LinkValidator:
    def __init__(self, timeout=5):
        self.timeout = timeout

    def validate_single(self, url):
        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=self.timeout
            )
            if response.status_code < 400:
                return url, True, "Alive"
            return url, False, f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return url, False, str(e)

    def validate_batch(self, links):
        results = {}
        for link in links:
            url, status, _ = self.validate_single(link)
            results[url] = status
        return results

    def filter_alive(self, validation_results):
        return [url for url, alive in validation_results.items() if alive]
