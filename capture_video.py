import csv
import os
import sys
from pathlib import Path

import qscript


def _field(row, key):
    value = row.get(key, "")
    return (value or "").strip()


def main(argv):
    csv_path = argv[1] if len(argv) > 1 else "input.csv"

    if not os.path.exists(csv_path):
        print(f"[capture_video] CSV not found: {csv_path}")
        return 1

    # Make sure the video folder exists and is absolute.
    video_dir = Path(qscript.PATH_TO_VIDEO_FOLDER).resolve()
    video_dir.mkdir(parents=True, exist_ok=True)
    qscript.PATH_TO_VIDEO_FOLDER = str(video_dir)

    total = 0
    ok = 0
    failed = 0

    with open(csv_path, "r", encoding="utf-8") as f:
        # skipinitialspace=True removes the spaces after each ';' so the
        # column names match exactly ("Company Name", not " Company Name").
        reader = csv.DictReader(
            f, delimiter=";", quotechar='"', skipinitialspace=True
        )
        for i, row in enumerate(reader, start=1):
            # Defensive: also strip any stray whitespace from the keys, so
            # the code is robust even if skipinitialspace is ever removed.
            row = {(k or "").strip(): v for k, v in row.items()}

            total += 1
            company_name = _field(row, "Company Name") or f"row_{i}"
            url = _field(row, "URL")

            print(f"\n[{i}] {company_name} -> {url}")
            try:
                result = qscript.CaptureVideo_Magento(
                    url=url,
                    company_name=company_name,
                    language=_field(row, "Language"),
                    country=_field(row, "Country"),
                    postcode=_field(row, "Postcode"),
                    city=_field(row, "City"),
                    street=_field(row, "Street"),
                    house_no=_field(row, "HouseNo"),
                )
            except Exception as e:
                print(f"    ERROR: {e}")
                failed += 1
                continue

            if result:
                print(f"    Saved: {result}")
                ok += 1
            else:
                print("    FAILED (no video)")
                failed += 1

    print(f"\nDone. rows={total} ok={ok} failed={failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))