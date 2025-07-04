import csv
import json
import time
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from question3.utils import process_url


class Command(BaseCommand):
    help = "Bulk-process images from a single URL or a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("--url", help="one image URL")
        parser.add_argument("--csv", help="CSV with image-URL rows")
        parser.add_argument(
            "--out", help="output JSON path (defaults to output_<ts>.json)"
        )

    def handle(self, *args, **opts):
        url, csv_file = opts["url"], opts["csv"]
        if not (url or csv_file):
            raise CommandError("Provide --url or --csv")

        urls = []
        if url:
            urls.append(url)
        if csv_file:
            with open(csv_file, newline="") as fh:
                urls += [
                    row[0].strip()
                    for row in csv.reader(fh)
                    if row and row[0].startswith(("http://", "https://"))
                ]
        if not urls:
            raise CommandError("No valid URLs supplied.")

        results = [process_url(u) for u in tqdm(urls, desc="processing")]

        outfile = (
            Path(opts["out"]) if opts["out"] else Path(f"output_{int(time.time())}.json")
        )
        outfile.write_text(json.dumps(results, indent=2))
        self.stdout.write(self.style.SUCCESS(f"Wrote {outfile} ({len(results)} records)"))
