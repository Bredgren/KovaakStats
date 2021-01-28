"""
MIT License

Copyright (c) 2021 Brandon Edgren

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
    "Pasu Voltaic Easy",
    "B180 Voltaic Easy",
    "Popcorn Voltaic Easy",
    "ww3t Voltaic",
    "1w4ts Voltaic",
    "6 Sphere Hipfire Voltaic",
    "Smoothbot Voltaic Easy",
    "Air Angelic 4 Voltaic Easy",
    "PGTI Voltaic Easy",
    "FuglaaXYZ Voltaic Easy",
    "Ground Plaza Voltaic Easy",
    "Air Voltaic Easy",
    "patTS Voltaic Easy",
    "psalmTS Voltaic Easy",
    "voxTS Voltaic Easy",
    "kinTS Voltaic Easy",
    "B180T Voltaic Easy",
    "Smoothbot TS Voltaic Easy",
]

def main():
    parser = argparse.ArgumentParser(
        description="Print data used for the Voltaic benchmarks progression spreadsheet.")
    parser.add_argument(
        "--statsdir", type=str, default=os.environ.get(STAT_DIR_ENV, None),
        help="File path to where the stat files are. This should be in "
        ".../SteamLibrary/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats. Defaults to the "
        "{} environment variable (currently: %(default)s)".format(STAT_DIR_ENV))
    def avgCheck(string):
        value = int(string)
        if value < 0:
            raise argparse.ArgumentTypeError("must not be a negative number")
        return value
    parser.add_argument(
        "--avg", type=avgCheck, default=10,
        help="The number of most recent runs to average. Use 0 to include all runs. "
        "Default: %(default)s")
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
    recent_avg = []
    for scenario in scenarios:
        if scenario not in files_by_challenge:
            personal_best.append(0)
            recent_avg.append(0)
            continue

        stats = parse_stats(args.statsdir, files_by_challenge[scenario])

        best = max(s.summary.score for s in stats)
        personal_best.append(best)

        if args.avg == 0:
            recent = stats
        else:
            recent = sorted(stats, key=lambda s: s.date, reverse=True)[:args.avg]
        scores = [s.summary.score for s in recent]
        avg = sum(scores) / len(scores)
        recent_avg.append(avg)

    print("Best:")
    print("\n".join("%.1f" % i for i in personal_best))
    print()

    if args.avg == 0:
        print("Average for all runs:")
    else:
        print(f"Average over {args.avg} most recent:")
    print("\n".join("%.1f" % i for i in recent_avg))
    print()

if __name__ == "__main__":
    main()
