"""Generate a fresh, explicitly synthetic two-order CSV example."""
import argparse
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from orders import FEED, REFERENCE


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    args.directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    now = datetime.now(timezone.utc)
    event = now.isoformat()
    approved = (now - timedelta(days=2)).isoformat()
    effective = (now - timedelta(days=1)).isoformat()
    orders, refs = [], []
    for name, quantity, unit in [("held", "20", "CASE"), ("clear", "240", "EA")]:
        order_id = "SYNTHETIC-" + name + "-" + now.strftime("%Y%m%dT%H%M%S%f")
        orders.append(["synthetic-csv-partner", order_id, order_id, "1", event, "SYNTHETIC-SKU", quantity, unit, "TEST"])
        refs.append(["synthetic-csv-partner", order_id, "1", "v1", effective, "", "synthetic-buyer", approved, "SYNTHETIC-SKU", "240", "EA", "TEST"])
    for filename, headers, rows in [("orders.csv", FEED, orders), ("approved.csv", REFERENCE, refs)]:
        path = args.directory / filename
        with path.open("x", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
        path.chmod(0o600)
    print("Created synthetic CSV orders and a separate synthetic approved export; no API calls.")


if __name__ == "__main__":
    main()
