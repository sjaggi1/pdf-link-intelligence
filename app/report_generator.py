import csv
import json
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    def __init__(self, output_dir="outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_csv_report(self, links, categorized, validation_results=None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.output_dir / f"links_report_{timestamp}.csv"

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Category", "Alive"])

            for category, urls in categorized.items():
                for url in urls:
                    alive = (
                        validation_results.get(url)
                        if validation_results
                        else "N/A"
                    )
                    writer.writerow([url, category, alive])

        return str(csv_path)

    def generate_json_summary(self, total_links, categorized, validation_results=None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.output_dir / f"summary_{timestamp}.json"

        summary = {
            "total_links": total_links,
            "categories": {k: len(v) for k, v in categorized.items()},
            "validation": validation_results or {},
            "generated_at": timestamp,
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)

        return str(json_path)

    def print_summary(self, categorized, validation_results=None):
        print("\n📊 Summary")
        for category, links in categorized.items():
            print(f"- {category}: {len(links)} links")

        if validation_results:
            alive = sum(1 for v in validation_results.values() if v)
            dead = len(validation_results) - alive
            print(f"✓ Alive: {alive}, ✗ Dead: {dead}")
