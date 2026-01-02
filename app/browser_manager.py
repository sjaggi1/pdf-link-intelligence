class BrowserManager:
    def __init__(self, batch_size=10, delay_minutes=0.5):
        self.batch_size = batch_size
        self.delay_minutes = delay_minutes

    def open_all_batches(self, links, interactive=False):
        for i in range(0, len(links), self.batch_size):
            batch = links[i:i + self.batch_size]
            print(f"Opening batch: {batch}")

    def dry_run(self, links):
        print("Dry run — links:")
        for link in links:
            print(link)
