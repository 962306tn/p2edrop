#!/usr/bin/env python3
"""Rename a creative library to the VelaHush naming convention + build a manifest.

Layout expected under --root (folder names are the tags):

    raw/
      TOF/VID/7R/*.mp4      TOF/IMG/MRC/*.jpg
      MOF/OWN/MECH/*.jpg
      BOF/OWN/OFFER/*.jpg

Output: files renamed in place to TIER_SOURCE_ANGLE_NNN.ext, plus manifest.csv
holding every asset with a status column that make_wave.py draws from.

Dry-run by default. Pass --apply to actually rename.
"""
import argparse, csv, sys
from pathlib import Path

TIERS = {"TOF", "MOF", "BOF"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MANIFEST_COLS = ["name", "tier", "source", "angle", "kind", "ext",
                 "rel_path", "status", "wave", "note"]


def scan(root: Path):
    """Yield (tier, source, angle, path) for every asset three levels deep."""
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel = path.relative_to(root)
        if len(rel.parts) != 4:
            print(f"  skip (wrong depth): {rel}", file=sys.stderr)
            continue
        tier, source, angle, _ = rel.parts
        tier, source, angle = tier.upper(), source.upper(), angle.upper()
        if tier not in TIERS:
            print(f"  skip (unknown tier {tier}): {rel}", file=sys.stderr)
            continue
        yield tier, source, angle, path


def kind_of(ext: str) -> str:
    if ext in VIDEO_EXT:
        return "video"
    if ext in IMAGE_EXT:
        return "image"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--manifest", type=Path, default=None,
                    help="default: <root>/manifest.csv")
    ap.add_argument("--apply", action="store_true", help="actually rename")
    args = ap.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")
    manifest_path = args.manifest or root / "manifest.csv"

    counters, rows, collisions = {}, [], 0
    for tier, source, angle, path in scan(root):
        bucket = (tier, source, angle)
        counters[bucket] = counters.get(bucket, 0) + 1
        ext = path.suffix.lower()
        name = f"{tier}_{source}_{angle}_{counters[bucket]:03d}{ext}"
        target = path.with_name(name)

        if target != path:
            if target.exists():
                print(f"  COLLISION, left alone: {target.name}", file=sys.stderr)
                collisions += 1
                name, target = path.name, path
            elif args.apply:
                path.rename(target)

        rows.append({
            "name": name, "tier": tier, "source": source, "angle": angle,
            "kind": kind_of(ext), "ext": ext,
            "rel_path": str(target.relative_to(root)),
            "status": "unused", "wave": "", "note": "",
        })

    if args.apply:
        with manifest_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=MANIFEST_COLS)
            writer.writeheader()
            writer.writerows(rows)

    print(f"\n{'RENAMED' if args.apply else 'DRY RUN'} — {len(rows)} assets")
    for bucket in sorted(counters):
        print(f"  {'/'.join(bucket):<20} {counters[bucket]:>4}")
    if collisions:
        print(f"\n  {collisions} collision(s) skipped — rerun after clearing them")
    if args.apply:
        print(f"\nmanifest → {manifest_path}")
    else:
        print("\nNothing written. Re-run with --apply.")


if __name__ == "__main__":
    main()
