#!/usr/bin/env python3
"""Draw the next weekly wave of creatives from manifest.csv.

Picks unused assets, fills the 3x3 TOF matrix plus MOF and BOF slots, and
writes a wave CSV whose columns match docs/velahush/build-sheet.csv so the
rows paste straight into the build sheet. Winners you keep running are never
drawn again — mark them status=winner and they stay out of later waves.

Dry-run by default. Pass --apply to write the wave file and update statuses.
"""
import argparse, csv, sys
from pathlib import Path

PDP = ("https://allvibespet.com/products/velahush-pet-odor-gun"
       "?variant=54327968235884&adv={adv}&cta=end")
ADV = "https://allvibespet.com/pages/velahush-{slug}"

ANGLES = {
    "7R":  {"slug": "7-reasons", "adv": "7-reasons-v2",
            "headline": "Pet smell keeps coming back? Here's why",
            "description": "Treats the surface, not the air"},
    "MRC": {"slug": "make-room-for-company", "adv": "make-room-v2",
            "headline": "Your pet belongs on the sofa. The smell doesn't.",
            "description": "Guest-ready in minutes"},
    "BSC": {"slug": "break-the-spray-bottle-cycle", "adv": "spray-cycle-v2",
            "headline": "Stop buying the same application problem in a new bottle",
            "description": "Fine mist, not a trigger sprayer"},
}
TOF_SOURCES = ["OWN", "IMG", "VID"]
ADSET = {"TOF": "AS{n} | TOF-{src} | Broad-AdvPlus",
         "MOF": "AS4 | MOF-WARM | PDP",
         "BOF": "AS5 | BOF-RTG14 | PDP"}
CAMPAIGN = {"TOF": "VH | TOF | CBO | US | 2026-09",
            "MOF": "VH | MOF | ABO | US | 2026-09",
            "BOF": "VH | BOF | ABO | US | 2026-09"}
OUT_COLS = ["Campaign", "AdSet", "AdName", "CreativeFile", "Kind",
            "Angle", "WebsiteURL", "Headline", "Description", "CTA"]


def take(pool, tier, source=None, angle=None, n=1):
    """Pop up to n unused rows matching the filters, oldest first."""
    picked = []
    for row in pool:
        if len(picked) == n:
            break
        if row["status"] != "unused" or row["tier"] != tier:
            continue
        if source and row["source"] != source:
            continue
        if angle and row["angle"] != angle:
            continue
        picked.append(row)
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--wave", required=True, type=int)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--mof", type=int, default=3, help="MOF ads this wave")
    ap.add_argument("--bof", type=int, default=1, help="BOF ads this wave")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows = list(csv.DictReader(args.manifest.open(encoding="utf-8")))
    if not rows:
        sys.exit("manifest is empty")

    out, gaps = [], []

    for idx, source in enumerate(TOF_SOURCES, start=1):
        for angle, meta in ANGLES.items():
            got = take(rows, "TOF", source=source, angle=angle, n=1)
            if not got:
                gaps.append(f"TOF/{source}/{angle}")
                continue
            asset = got[0]
            asset["status"], asset["wave"] = "queued", args.wave
            out.append({
                "Campaign": CAMPAIGN["TOF"],
                "AdSet": ADSET["TOF"].format(n=idx, src=source),
                "AdName": f"W{args.wave}_TOF{idx}_{source}_{angle}",
                "CreativeFile": asset["name"], "Kind": asset["kind"],
                "Angle": angle,
                "WebsiteURL": ADV.format(slug=meta["slug"]),
                "Headline": meta["headline"],
                "Description": meta["description"], "CTA": "LEARN_MORE",
            })

    for tier, count, cta in (("MOF", args.mof, "SHOP_NOW"),
                             ("BOF", args.bof, "SHOP_NOW")):
        picked = take(rows, tier, n=count)
        if len(picked) < count:
            gaps.append(f"{tier} (wanted {count}, got {len(picked)})")
        for asset in picked:
            asset["status"], asset["wave"] = "queued", args.wave
            meta = ANGLES.get(asset["angle"])
            adv = meta["adv"] if meta else "7-reasons-v2"
            out.append({
                "Campaign": CAMPAIGN[tier], "AdSet": ADSET[tier],
                "AdName": f"W{args.wave}_{asset['name'].rsplit('.', 1)[0]}",
                "CreativeFile": asset["name"], "Kind": asset["kind"],
                "Angle": asset["angle"],
                "WebsiteURL": PDP.format(adv=adv),
                "Headline": meta["headline"] if meta else "",
                "Description": meta["description"] if meta else "", "CTA": cta,
            })

    out_path = args.out or args.manifest.with_name(f"wave-{args.wave}.csv")
    if args.apply:
        with out_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=OUT_COLS)
            writer.writeheader()
            writer.writerows(out)
        with args.manifest.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    left = sum(1 for r in rows if r["status"] == "unused")
    print(f"\n{'WROTE' if args.apply else 'DRY RUN'} wave {args.wave} — {len(out)} ads")
    for row in out:
        print(f"  {row['AdName']:<26} {row['CreativeFile']}")
    if gaps:
        print("\n  EMPTY BUCKETS (fill these or the matrix has holes):")
        for gap in gaps:
            print(f"    - {gap}")
    print(f"\n  {left} assets still unused")
    print(f"\nwave → {out_path}" if args.apply
          else "\nNothing written. Re-run with --apply.")


if __name__ == "__main__":
    main()
