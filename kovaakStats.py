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
from collections import defaultdict, namedtuple
import csv
from datetime import datetime
import os
from os import path
# from pprint import pprint, pformat
import re

from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
# import numpy

STAT_DIR_ENV = "KOVAAK_STAT_DIR"
IMG_DIR_ENV = "KOVAAK_STAT_IMG_DIR"

STAT_FILE_RE = re.compile(r"(?P<name>.+) - Challenge - (?P<date>.+) Stats\.csv")

class SessionStat(object):
    """Stats for a single session. """

    Summary = namedtuple("Summary", ["kills", "deaths", "fight_time", "avg_ttk", "damage_done",
                                     "damage_taken", "score", "game_version"])
    Kill = namedtuple("Kill", ["kill", "timestamp", "bot", "weapon", "ttk", "shots", "hits",
                               "accuracy", "damage_done", "damage_possible", "efficiency",
                               "cheated"])
    Weapon = namedtuple("Weapon", ["weapon", "shots", "hits", "damage_done", "damage_possible"])

    def __init__(self, date, summary, kills, weapons):
        self.date = date
        self.summary = summary
        self.kills = kills
        self.weapons = weapons

    @property
    def accuracy(self):
        total_shots, total_hits = 0, 0
        for kill in self.kills:
            total_shots += kill.shots
            total_hits += kill.hits
        if total_shots == 0:
            return 0
        return total_hits / total_shots

    @property
    def ttk(self):
        total_ttk = 0
        for kill1, kill2 in zip(self.kills, self.kills[1:]):
            total_ttk += (kill2.timestamp - kill1.timestamp).total_seconds()
        if len(self.kills) <= 1:
            return 0
        return total_ttk / (len(self.kills) - 1)

    @staticmethod
    def from_file(fname):
        m = STAT_FILE_RE.match(fname)
        date = datetime.strptime(m.group("date"), "%Y.%m.%d-%H.%M.%S")
        with open(fname, "r") as f:
            kill_csv, weapon_csv, summary_csv, settings_csv = f.read().split("\n\n")

        summary_info = {row[0].strip(":"): row[1] for row in csv.reader(summary_csv.splitlines())}

        score_offset = -99000 if "Ground Plaza NO UFO" in m.group("name") else 0

        summary = SessionStat.Summary(
            int(summary_info["Kills"]),
            int(summary_info["Deaths"]),
            float(summary_info["Fight Time"]),
            float(summary_info["Avg TTK"]),
            float(summary_info["Damage Done"]),
            float(summary_info["Damage Taken"]),
            float(summary_info["Score"]) + score_offset,
            tuple(map(int, summary_info["Game Version"].split("."))))

        timestamp_format = "%H:%M:%S:%f" if summary.game_version < (2, 0, 1, 0) else "%H:%M:%S.%f"

        kills = []
        reader = csv.DictReader(kill_csv.splitlines())
        for row in reader:
            kills.append(SessionStat.Kill(
                int(row["Kill #"]),
                datetime.strptime(row["Timestamp"], timestamp_format),
                row["Bot"],
                row["Weapon"],
                float(row["TTK"][:-1]),
                int(row["Shots"]),
                int(row["Hits"]),
                float(row["Accuracy"]),
                float(row["Damage Done"]),
                float(row["Damage Possible"]),
                float(row["Efficiency"]),
                bool(row["Cheated"])))

        weapons = []
        reader = csv.DictReader(weapon_csv.splitlines())
        for row in reader:
            weapons.append(SessionStat.Weapon(
                row["Weapon"],
                int(row["Shots"]),
                int(row["Hits"]),
                float(row["Damage Done"]),
                float(row["Damage Possible"])))

        # TODO: Skipping this for now. Not sure if it's useful.
        _ = settings_csv

        return SessionStat(date, summary, kills, weapons)

def daily_stats(stats, get_stat):
    days, values = [], []

    stats_by_day = defaultdict(list)
    for stat in sorted(stats, key=lambda s: s.date):
        day = stat.date.strftime("%Y-%m-%d")
        if day not in days:
            days.append(day)
        stats_by_day[day].append(stat)

    for day in days:
        avg = sum(get_stat(s) for s in stats_by_day[day]) / len(stats_by_day[day])
        values.append(avg)

    return days, values

# For making box plots.
# def daily_stats2(stats, get_stat):
#     days, values = [], []

#     stats_by_day = defaultdict(list)
#     for stat in sorted(stats, key=lambda s: s.date):
#         day = stat.date.strftime("%Y-%m-%d")
#         if day not in days:
#             days.append(day)
#         stats_by_day[day].append(get_stat(stat))

#     for day in days:
#         values.append(stats_by_day[day])

#     return days, values

def parse_stats(stats_dir, stat_files):
    return [SessionStat.from_file(path.join(stats_dir, f)) for f in stat_files]

# def _trendline(ax, x, y):
#     z = numpy.polyfit(x, y, 1)
#     p = numpy.poly1d(z)
#     ax.plot(x,p(x), "r--")

def _conf_axes(axes, title, rotate):
    axes.set_title(title)
    axes.grid(True)
    if rotate:
        plt.setp(axes.get_xticklabels(), rotation=40, ha="right", rotation_mode="anchor")

def plot_tracking(challenge_name, fig_id, stats, img_dir):
    width, height = 1, 2

    fig = plt.figure(fig_id, figsize=(20, 12))
    fig.suptitle(challenge_name)

    ax = plt.subplot(height, width, 1)
    _conf_axes(ax, "Score", False)
    x, y = zip(*enumerate(s.summary.score for s in stats))
    ax.plot(x, y, ".")
    # _trendline(ax, x, y)

    ax = plt.subplot(height, width, 2)
    _conf_axes(ax, "Avg Score Per Day", True)
    ax.scatter(*daily_stats(stats, lambda s: s.summary.score))

    # ax.set_title("Avg Score Per Day")
    # days, values = daily_stats2(stats, lambda s: s.summary.score)
    # for _, value in zip(days, values):
    #     plt.boxplot(values)
    # ax.set_xticklabels(days, rotation=45)

    # plt.show()
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(path.join(img_dir, challenge_name))
    print("Saved", path.join(img_dir, challenge_name) + ".png")

    plt.close(fig)

def plot_click_timing(challenge_name, fig_id, stats, img_dir):
    width, height = 2, 4

    fig = plt.figure(fig_id, figsize=(20, 12))
    fig.suptitle(challenge_name)

    ax = plt.subplot(height, width, 1)
    _conf_axes(ax, "Score", False)
    x, y = zip(*enumerate(s.summary.score for s in stats))
    ax.plot(x, y, ".")
    # _trendline(ax, x, y)

    ax = plt.subplot(height, width, 3)
    _conf_axes(ax, "Avg Score Per Day", True)
    days, values = daily_stats(stats, lambda s: s.summary.score)
    ax.scatter(days, values)
    # _trendline(ax, range(len(days)), values)

    ax = plt.subplot(height, width, 2)
    _conf_axes(ax, "Kills", False)
    ax.plot([s.summary.kills for s in stats], ".")

    ax = plt.subplot(height, width, 4)
    _conf_axes(ax, "Avg Kills Per Day", True)
    ax.scatter(*daily_stats(stats, lambda s: s.summary.kills))

    ax = plt.subplot(height, width, 6)
    _conf_axes(ax, "Accuracy", False)
    ax.plot([s.accuracy for s in stats], ".")

    ax = plt.subplot(height, width, 8)
    _conf_axes(ax, "Avg Accuracy Per Day", True)
    ax.scatter(*daily_stats(stats, lambda s: s.accuracy))

    ax = plt.subplot(height, width, 5)
    _conf_axes(ax, "TTK", False)
    ax.plot([s.ttk for s in stats], ".")

    ax = plt.subplot(height, width, 7)
    _conf_axes(ax, "Avg TTK Per Day", True)
    ax.scatter(*daily_stats(stats, lambda s: s.ttk))

    plt.subplots_adjust(top=0.95, bottom=0.08, left=0.05, right=0.95, hspace=0.5, wspace=0.2)

    # plt.show()
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(path.join(img_dir, challenge_name))
    print("Saved", path.join(img_dir, challenge_name) + ".png")

    plt.close(fig)

def main():
    parser = argparse.ArgumentParser(description="Generate graphs from Kovaak data.")
    parser.add_argument(
        "--statsdir", type=str, default=os.environ.get(STAT_DIR_ENV, None),
        help="File path to where the stat files are. This should be in "
        ".../SteamLibrary/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats. Defaults to the "
        "{} environment variable (currently: %(default)s)".format(STAT_DIR_ENV))
    parser.add_argument(
        "--imgdir", type=str, default=os.environ.get(IMG_DIR_ENV, None),
        help="File path to save the generated images at. Defaults to the "
        "{} environment variable (currently: %(default)s)".format(IMG_DIR_ENV))
    args = parser.parse_args()

    if not args.statsdir:
        print("Please use the --statdir option or set the %s environment variable." % STAT_DIR_ENV)
        exit(1)
    if not args.imgdir:
        print("Please use the --imgdir option or set the %s environment variable." % IMG_DIR_ENV)
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

    # challenges = sorted(files_by_challenge.keys())
    # print("\n".join("%d: %s" % (i + 1, c) for i, c in enumerate(challenges)))

    # def _request_digit():
    #     choice = input("Select challenge: ")
    #     if not choice.isdigit() or not 1 <= int(choice) <= len(challenges):
    #         print("Please enter a number in range 1-%d" % len(challenges))
    #         return None
    #     return choice

    # choice = _request_digit()
    # while not choice:
    #     choice = _request_digit()

    # challenge_name = challenges[int(choice) - 1]

    # stats = parse_stats(stats_dir, files_by_challenge[challenge_name])

    # if stats[0].summary.kills > 0:
    #     plot_click_timing(challenge_name, stats, img_dir)
    # else:
    #     plot_tracking(challenge_name, stats, img_dir)

    fig_id = 1
    for challenge_name, files in files_by_challenge.items():
        stats = parse_stats(args.statsdir, files)

        if stats[0].summary.kills > 0:
            plot_click_timing(challenge_name, fig_id, stats, args.imgdir)
        else:
            plot_tracking(challenge_name, fig_id, stats, args.imgdir)

        fig_id += 1

if __name__ == "__main__":
    main()
