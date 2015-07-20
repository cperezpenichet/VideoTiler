# VideoTiler
Tile videos side by side with optional time synchronization.

This script uses the MLT framework (www.mltframework.org) through its
CLI interface tool (melt) to create a composition of two videos where 
they are displayed side by side. Optionally synchronization pauses can
be introduced in either or both of the videos to keep them synchronized.

# Usage 
video_tiler.py [-h] [-o OUTPUT] videoA videoB [synchList]

positional arguments:
  videoA                The first video to tile. It will appear on the left
  videoB                The second video to tile. It will appear on the right
  synchList             File containing the synchronization points if any

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Name of the output file. Display preview if absent

 The synchronization list file (synchList) should contain a list of pauses,
one per line. Each pause consists of two numbers separated by a |TAB|.

ex: A_1|TAB|B_1

This indicated that frame A_1 in of videoA corresponds to frame B_1 in videoB
the script will introduce a pause in one of the videos (the one running ahead)
in to make the indicated frames match. This will be repeated for every pause 
indicated in the synchList file.

 Using the script in preview mode (without the --output option) can be helpful
for creating the synchronization list.


# Dependencies:

- The mlt framework. Ubuntu package: melt
- The frei0r video effects plugin collection. Ubuntu package: frei0r-plugins
- Mplayer to retrieve the video frame rate (and others?) Ubuntu package: mplayer2

# Roadmap:

* Need to generalize so that it works with videos of any size.
* There might be other dependencies, check and try and reduce the number of dependencies
* Try to generalize so that it works with any (reasonable) number of videos, not just two
