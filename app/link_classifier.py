class LinkClassifier:
    def __init__(self):
        pass

    def classify(self, link: str) -> str:
        link = link.lower()
        if "github.com" in link:
            return "github"
        if "linkedin.com" in link:
            return "linkedin"
        if "portfolio" in link:
            return "portfolio"
        return "other"

    def classify_batch(self, links):
        categorized = {}
        for link in links:
            category = self.classify(link)
            categorized.setdefault(category, []).append(link)
        return categorized

    def get_priority_sorted(self, categorized, priority=None):
        if not priority:
            return categorized.items()
        return sorted(
            categorized.items(),
            key=lambda x: priority.index(x[0]) if x[0] in priority else len(priority)
        )
