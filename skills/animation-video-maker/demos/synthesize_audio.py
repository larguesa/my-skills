#!/usr/bin/env python3
"""Original local sound bed and lossless-video mux. No model calls."""
import argparse
import subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('silent_source', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
if a.output.exists():
    p.error('Output exists; choose a new path or explicitly remove it first.')
# A slow A/E suspended dyad with periodic amplitude and a quiet octave.
# No sampled material. Stereo separation is synthesized algebraically.
expression = ('0.085*(0.65+0.35*cos(2*PI*t/8))*sin(2*PI*110*t)'
              '+0.038*sin(2*PI*164.813778*t)+0.018*sin(2*PI*220*t)')
source = f'aevalsrc={expression}|{expression.replace("110*t", "110*t+0.12")}:s=48000:d=8'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin',
                '-i',str(a.silent_source),'-f','lavfi','-i',source,
                '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac',
                '-b:a','160k','-af','afade=t=in:d=0.6,afade=t=out:st=7:d=1',
                '-t','8','-movflags','+faststart',str(a.output)],check=True)
print(a.output)
