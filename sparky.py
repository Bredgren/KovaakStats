"""
MIT License

Copyright (c) 2020 Brandon Edgren

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
from collections import defaultdict
import os

from kovaakStats import (
    STAT_DIR_ENV,
    STAT_FILE_RE,
    parse_stats,
)

scenarios = [
    "1wall5targets_pasu Reload",
    "Popcorn Sparky",
    "Wide Wall 6Targets",
    "1wall 6targets small",
    "Bounce 180 Sparky",
    "Air no UFO no SKYBOTS",
    "Ground Plaza NO UFO",
    "Popcorn Goated Tracking Invincible",
    "Thin Gauntlet V2",
    "Pasu Track Invincible v2",
    "patTargetSwitch",
    "Bounce 180 Tracking",
    "kinTargetSwitch",
    "devTargetSwitch Goated",
    "voxTargetSwitch",
    "Air Dodge",
    "Pasu Dodge Easy",
    "Pistol Strafe Gallery Sparky",
    "lgc3 Reborn",
    "patTargetSwitch Dodge 360 v2",
]

def main():
    parser = argparse.ArgumentParser(
        description="Print data used for the Sparky Aimtraining progression spreadsheet.")
    parser.add_argument(
        "--statsdir", type=str, default=os.environ.get(STAT_DIR_ENV, None),
        help="File path to where the stat files are. This should be in "
        ".../SteamLibrary/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats. Defaults to the "
        "{} environment variable (currently: %(default)s)".format(STAT_DIR_ENV))
    args = parser.parse_args()

    if not args.statsdir:
        print("Please use the --statdir option or set the %s environment variable." % STAT_DIR_ENV)
        exit(1)

    all_stat_files = []
    for _, _, files in os.walk(args.statsdir):
        all_stat_files += files

    files_by_challenge = defaultdict(list)
    for fname in all_stat_files:
        m = STAT_FILE_RE.match(fname)
        if not m:
            continue
        files_by_challenge[m.group("name")].append(fname)

    personal_best = []
    most_recent = []
    for scenario in scenarios:
        if scenario not in files_by_challenge:
            personal_best.append(0)
            most_recent.append([0] * 5)
            continue

        stats = parse_stats(args.statsdir, files_by_challenge[scenario])

        best = max(s.summary.score for s in stats)
        personal_best.append(best)

        recent = sorted(stats, key=lambda s: s.date, reverse=True)[:5]
        scores = [s.summary.score for s in recent]
        pad = 5 - len(scores)
        scores += [0] * pad
        most_recent.append(scores)

    print("Best:")
    print("\n".join("%.1f" % i for i in personal_best))
    print()

    print("5 Most Recent:")
    for recents in most_recent:
        print(("{:<10.1f}" * 5).format(*recents))

if __name__ == "__main__":
    main()
