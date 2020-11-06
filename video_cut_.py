# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 15:40:37 2020

@author: Wells Wang
"""
# pip install webrtcvad_wheels (windows)
# pip install pysrt

import pathlib
import pysrt
from subprocess import run
import config as cfg
ffmpeg=cfg.ffmpeg_bin
input_video_file="E:\\testvideo\\IMG_1066.mov"
outpath=str(pathlib.Path(input_video_file).parents[0])

inp_srt_file=pathlib.Path(input_video_file).stem+".srt"
inp_srt_file=pathlib.Path(outpath) /inp_srt_file
split_file_name=pathlib.Path(input_video_file).stem
split_file_name=pathlib.Path(outpath)/split_file_name
outvideo=f"{outpath}/mergeoutname.mov"

stt=""
edt=""
out=""

videostr=pysrt.open(inp_srt_file)
#for sub in enumerate(videostr):
tmp_out_names=[]    
for sub in videostr:
    print(str(sub.start),str(sub.end))
    outname=f"{split_file_name}_{sub.index}.mov"
    #outname=f"{outpath}/{outname}.mov"
    
    st_time=timer=sub.start.to_time().strftime("%H:%M:%S.%f")
    ed_time=timer=sub.end.to_time().strftime("%H:%M:%S.%f")
    # copy mode 
    a_codec="copy"
    v_codec="copy"
    codec_mode=f"-acodec {a_codec} -vcodec {v_codec}"
    ffmpeg_params=f"{ffmpeg} -i {input_video_file} -ss {st_time} -t {ed_time} {codec_mode} -async 1 {outname} -y"
    print(ffmpeg_params)
    tmp_out_names.append(outname)
    ffmpeg_params=ffmpeg_params.split()
    res=run(ffmpeg_params )

"""
_tmp_out_names="|".join(tmp_out_names)
contact_params=f"concat:{_tmp_out_names}"
#ffmpeg -i "concat:input1|input2" -codec copy output.mkv
ffmpeg_cmds=f'{ffmpeg} -i "{contact_params}" -codec copy {outvideo} -y'
print(ffmpeg_cmds)
ffmpeg_cmds=ffmpeg_cmds.split()
#res=run(ffmpeg_cmds )
"""

##Video Merge ffmpeg script parameter generator
inp=''
vidf=""
vfilt='-filter_complex'
for idx,item in enumerate(tmp_out_names):
    inp=f'{inp} -i "{item}" '
    vidf=f'{vidf} [{idx}:v] [{idx}:a]'
param3=f'concat=n={len(tmp_out_names)}:v=1:a=1 [v] [a]'
param4=f'-map "[v]" -map "[a]"'
vidf=vidf.strip()
ffmpg_cmd=f'{ffmpeg} {inp} {vfilt} "{vidf} {param3}" {param4}  {outvideo} -y'
print("---copy below ffmpeg script ..to cmd console--------")
print(ffmpg_cmd)
#ffmpg_cmd=ffmpg_cmd.split()
#res=run(ffmpg_cmd )
