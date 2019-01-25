'''
How to use
'''

from __future__ import print_function
import time
import os
import re
from io import BytesIO
from cStringIO import StringIO

from ocr import OCR
from base_assistant import run_assistant, movenames

import wda
from threes import do_move

re_sshot = r'^S_(\d{6}).png$'
fmt_sshot = r'S_%06d.png'

def playback_gesture(s, move):
    print(move)
    return {
        "left": s.swipe_left(),
        "right": s.swipe_right(),
        "up": s.swipe_up(),
        "down": s.swipe_down()
      }[move]
    
    

class IOSAssistant:
    def __init__(self, client, session, ocr):
        self.client = client
        self.session = session
        self.ocr = ocr
        self.last_board = None

    def gen_board_mem(self):
        while True:
            sshot_data = self.client.screenshot('hehe.png')
            sshot_file = StringIO(sshot_data)
            board, tileset = self.ocr.ocr(sshot_file)
            self.last_board = board
            yield board, tileset, False

    def gen_board_disk(self, d, resume=False):
        curnum = 0
        if resume:
            imglist = sorted([fn for fn in os.listdir(d) if re.match(re_sshot, fn)])
            if imglist:
                last = imglist[-1]
                for fn in imglist:
                    print(fn)
                    board, tileset = self.ocr.ocr(os.path.join(d, fn))
                    skip = (fn != last)
                    self.last_board = board
                    yield board, tileset, skip
                curnum = int(re.match(re_sshot, last).group(1), 10)+1

        while True:
            sshot_file = self.client.screenshot('hehe.png')
            board, tileset = self.ocr.ocr(sshot_file)
            if board is None:
                # Wait a bit and retry
                print("Retrying screenshot...")
                time.sleep(5)
                continue

            fn = fmt_sshot % curnum
            dfn = os.path.join(d, fn)
            curnum += 1
            with open(dfn, 'wb') as f:
                f.write(sshot_data)
            print(fn)
            self.last_board = board
            yield board, tileset, False

    def make_move(self, move):
        playback_gesture(self.session, move)

        sleeptime = 1.0
        if self.last_board is not None:
            board = self.last_board.copy()
            do_move(board, movenames.index(move))
            top = board.max()
            if sorted(self.last_board.flatten()) == sorted(board.flatten()):
                # No new tiles at all: no flipping or jumping
                sleeptime = 0.5
            elif top <= 3 or list(self.last_board.flatten()).count(top) == list(board.flatten()).count(top):
                # No new high tile created, so no jumping will occur.
                sleeptime = 0.5
            else:
                # The new high tile will jump; wait for a long time for jump animation to finish.
                sleeptime = 1.0

        time.sleep(sleeptime)

    def restart(self):
        ''' Restart from the "out of moves" screen '''
        playback_gesture(self.session, 'right') # swipe to see your score
        time.sleep(0.5)
        playback_gesture(self.session, 'left') # skip the score counting
        time.sleep(2)
        playback_gesture(self.session, 'right') # swipe to save your score
        time.sleep(2)
        playback_gesture(self.session, 'left') # swipe from score to menu
        time.sleep(2)
        # playback_gesture(self.session, 'pressbutton') # press Main Menu button
        # time.sleep(2)
        # playback_gesture(self.session, 'pressbutton') # press Play Threes button
        # time.sleep(2.0)
        self.last_board = None

def parse_args(argv):
    import argparse
    parser = argparse.ArgumentParser(description="Control Threes! running on an iPhone")
    parser.add_argument('--no-resume', action='store_false', dest='resume', default=True, help="Don't resume from previous data")
    parser.add_argument('--from-start', action='store_true', default=False, help="Assume that the game starts from the initial state. May improve performance.")
    parser.add_argument('--repeat', action='store_true', default=False, help="Repeat games indefinitely")
    parser.add_argument('outdir', nargs='?', help="Output directory for screen captures (interpreted as a prefix if repeat is on)")

    args = parser.parse_args(argv)
    return args

def main(argv):
    from itertools import count
    args = parse_args(argv)

    client = wda.Client('http://localhost:8100')
    session = client.session('vo.threes.free')
    model = "iphone"

    assistant = IOSAssistant(client, session, OCR(model))

    if args.repeat:
        iterations = count(1)
    else:
        iterations = ['']

    for i,suffix in enumerate(iterations):
        if i >= 1:
            assistant.restart()
        if args.outdir:
            outdir = args.outdir + str(suffix)
            try:
                os.makedirs(outdir)
            except OSError:
                pass
            run_assistant(assistant.gen_board_disk(outdir, args.resume), assistant.make_move, args.from_start)
        else:
            run_assistant(assistant.gen_board_mem(), assistant.make_move, args.from_start)

if __name__ == '__main__':
    import sys
    exit(main(sys.argv[1:]))
