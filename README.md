# KovaakStats
A simple python program that will parse the csv files that Kovaak 2.0: The Meta creates and generate
graphs of multiple stats for each scenario.

# Dependencies
You will need to install the following:
* [python3](https://www.python.org/downloads/)
* [matplotlib](https://matplotlib.org/users/installing.html)

# Usage
Run the python script kovaakStats.py to generate the graphs. It will need two pieces of information
to work: the location of the stat files, and where you want the images to be saved to. These can be
provided either through command line arguments or as environment variables.
```
> python kovaakStats.py -h
usage: kovaakStats.py [-h] [--statsdir STATSDIR] [--imgdir IMGDIR]

Generate graphs from Kovaak data.

optional arguments:
  -h, --help           show this help message and exit
  --statsdir STATSDIR  File path to where the stat files are. This should be
                       in .../SteamLibrary/steamapps/common/FPSAimTrainer/FPSA
                       imTrainer/stats. Defaults to the KOVAAK_STAT_DIR
                       environment variable (currently: G:\SteamLibrary\steama
                       pps\common\FPSAimTrainer\FPSAimTrainer\stats)
  --imgdir IMGDIR      File path to save the generated images at. Defaults to
                       the KOVAAK_STAT_IMG_DIR environment variable
                       (currently: D:\Pictures\Kovaak)
```

# Example output
![ex1](https://github.com/Bredgren/KovaakStats/blob/master/examples/1wall6targets%20TE.png)
![ex2](https://github.com/Bredgren/KovaakStats/blob/master/examples/Vertical%20Long%20Strafes.png)
