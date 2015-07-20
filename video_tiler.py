#!/usr/bin/python

# 
# Video file tiler. Tile two videos side by side with optional time
# synchronization.
#
# Copyright (C) 2015 Carlos Penichet <cperezpenichet@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

#
#  This script uses the MLT framework (www.mltframework.org) through its
# CLI interface tool (melt) to create a composition of two videos where 
# they are displayed side by side. Optionally synchronization pauses can
# be introduced in either or both of the videos to keep them synchronized.
#
# Usage: video_tiler.py [-h] [-o OUTPUT] videoA videoB [synchList]
# 
# Tile two videos side by side with optional time synchronization.
# 
# positional arguments:
#   videoA                The first video to tile. It will appear on the left
#   videoB                The second video to tile. It will appear on the right
#   synchList             File containing the synchronization points if any
# 
# optional arguments:
#   -h, --help            show this help message and exit
#   -o OUTPUT, --output OUTPUT
#                         Name of the output file. Display preview if absent
# 
#  The synchronization list file (synchList) should contain a list of pauses,
# one per line. Each pause consists of two numbers separated by a <TAB>.
#
# ex: A_1<TAB>B_1
#
# This indicated that frame A_1 in of videoA corresponds to frame B_1 in videoB
# the script will introduce a pause in one of the videos (the one running ahead)
# in to make the indicated frames match. This will be repeated for every pause 
# indicated in the synchList file.
#
#  Using the script in preview mode (without the --output option) can be helpful
# for creating the synchronization list.

#
#  Dependencies:
#
# - The mlt framework. Ubuntu package: melt
# - The frei0r video effects plugin collection. Ubuntu package: frei0r-plugins
# - Mplayer to retrieve the video frame rate (and others?) Ubuntu package: mplayer2
#
# TODO: There might be other dependencies, check.
# TODO: Try and reduce the number of dependencies

# TODO: Try to generalize so that it works with any (reasonable) number of videos.
# TODO: Need to generalize so that it works with videos of any size.

import argparse
import csv
from subprocess import call
import subprocess
from re import compile as re_compile

OUTPUT = '-consumer avformat:{:s} mlt_profile=hdv_720_30p an=1 vcodec=libx264 frame_rate_num={:d} frame_rate_den=1'
PREVIEW_OUTPUT = '-consumer fps={:f}'

MELT_INVOCATION = 'melt'

MELT_TRACK = '-track'
AFFINE_FILTER_STR = '-filter affine transition.geometry={:s}'
AFFINE_TRANSITION_STR = '-attach crop left=320 -transition affine geometry={:s}'
GEOMETRY_L = '"-25%/0%:100%x100%:100%"'
GEOMETRY_R = '"37.5%/0%:100%x100%:100%"'

MELT_GROUP = '-group'
MELT_IN = 'in={:d}'
TIMEDELAY_FILTER = '-filter frei0r.delay0r DelayTime={:.2f}'

def cli_parse():
    '''Parse CLI options.'''
    parser = argparse.ArgumentParser(description='Tile two videos side by side with optional time synchronization.')
    parser.add_argument('videoA',
            help='The first video to tile. It will appear on the left')
    parser.add_argument('videoB',
            help='The second video to tile. It will appear on the right')
    parser.add_argument('synchList', nargs='?', default=None,
            help='File containing the synchronization points if any')
    parser.add_argument('-o', '--output', required=False,
            help='Name of the output file. Display preview if absent')
    return parser.parse_args()

def prepare_delays(pauses, FPS):
    '''Prepare delay command line to Melt based on a list of pauses'''
    ret = list()
    for pause in pauses:
        ret.extend([
                MELT_GROUP,
                MELT_IN.format(min(pause[0], pause[-1])),
                TIMEDELAY_FILTER.format(abs(float(pause[-1]-pause[0])/FPS))
                ])
    if len(pauses) > 0:
        ret.append(MELT_GROUP)
    return ret

def get_fps(movie_file):
    '''Determine the frame rate of a video using mplayer'''
    pattern = re_compile(r'ID_VIDEO_FPS=(\d{2}.\d{3})')
    mp_output = subprocess.Popen((
        'mplayer',
        '-identify',
        '-frames',
        '0',
        'o-ao',
        'null',
        movie_file
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        ).communicate()[0]
    fps = pattern.search(mp_output).groups()[0]
    return float(fps)

def main():
    args = cli_parse()

    fps_A = get_fps(args.videoA)
    fps_B = get_fps(args.videoB)

    a_pauses = list()
    b_pauses = list()
    if args.synchList:
        with open(args.synchList) as synchFile:
            timereader = csv.reader(synchFile, dialect='excel-tab')
            for row in timereader:
                row = map(int, row)
                if row[0] < row[-1]:
                    a_pauses.append(tuple(row))
                else:
                    b_pauses.append(tuple(row))


    command_list = list()
    command_list.extend([
        MELT_INVOCATION,

        MELT_TRACK,
        args.videoA,
        AFFINE_FILTER_STR.format(GEOMETRY_L),
        ])

    command_list.extend(prepare_delays(a_pauses, fps_A))

    command_list.extend([
        MELT_TRACK,
        args.videoB,
        AFFINE_TRANSITION_STR.format(GEOMETRY_R)
        ])

    command_list.extend(prepare_delays(b_pauses, fps_B))

    if args.output:
        command_list.append(OUTPUT.format(args.output, int(max(fps_A, fps_B)))) 
    else:
        command_list.append(PREVIEW_OUTPUT.format(max(fps_A, fps_B)))

    print " ".join(command_list)
    call(' '.join(command_list), shell=True) # For some reason it has to be called with shell and join otherwise it doesn't work properly.

if __name__ == '__main__':
    main()
