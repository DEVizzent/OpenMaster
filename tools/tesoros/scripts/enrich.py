import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.enricher import Enricher

ITEMS_PATH = Path(__file__).parent.parent / "items.json"


def main():
    dry_run = "--dry-run" in sys.argv

    enricher = Enricher(ITEMS_PATH)
    enricher.enrich(dry_run=dry_run)


if __name__ == "__main__":
    main()
