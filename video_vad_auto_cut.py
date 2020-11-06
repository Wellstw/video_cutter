# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 12:48:53 2020

@author: wells Wang
@description , extract audio track from video file
and use speech detect and create srt file
"""


import tempfile
import pathlib
from subprocess import run
import video_speech_mark as vmark
import time
import click
import config as cfg

#python -m pip install webrtcvad-wheels

ffmpeg=cfg.ffmpeg_bin
ffmpeg_audio_extract=cfg.ffmpeg_audio_extract

input_video_file="E:\\testvideo\\IMG_1066.mov"

outpath=str(pathlib.Path(input_video_file).parents[0])
out_srt_file=pathlib.Path(input_video_file).stem+".srt"
out_srt_file=pathlib.Path(outpath) /out_srt_file

audio_temp_file=pathlib.Path(input_video_file).stem+".wav"
audio_temp_file=pathlib.Path(outpath) /audio_temp_file



extract_audio_cmd=f"{ffmpeg} -i {input_video_file} {ffmpeg_audio_extract} {audio_temp_file} -y"
extract_audio_cmd=extract_audio_cmd.split()
res=run(extract_audio_cmd )
if res.returncode !=0:
    print(res.stderr)
time.sleep(0.1)
vmark.speech_detect(inpfile=str(audio_temp_file),srtout=out_srt_file)
