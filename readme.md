## youtuber 剪片神器
這是一個使用 webrtcvad 做成的 剪片神器
對於談話性影片的製作提供一個自動切割整合的工具及可利用subtitle editor 微調

webrtcvad 是一個 可以用來偵測語音裡哪些部份有人聲
這個
再配合 pysrt 做的 srt 檔
後續可以使用 subtitle editor 做微調
再配合使用 video_cut_.py(ffmpeg) 做為切割
及產生 ffmpeg 的自動合併 腳本 , 使用者可以直接 copy 到
cmd(windows) 或 shell(linux) 下面直接執行


#### Installation 
這個程式是由 webrtcvad 裡的 example.py 修改而來
需要先安修下列依赖包
Windows/Winpython 3.7
python -m pip install webrtcvad-wheels
python -m pip install pysrt
python -m pip install click

ubuntu 請安裝 
pip install webrtcvad
pip install pysrt
pip install click

#### 其他配合程式
subtitle editor 
https://github.com/SubtitleEdit/subtitleedit/releases
windows ffmpeg
https://github.com/BtbN/FFmpeg-Builds/releases
#### 使用方式
請在 config.py 指定你的 ffmpeg 的路徑
ffmpeg_bin="C:\\portableApp\\ffmpeg\\bin\\ffmpeg.exe"
在 video_vad_auto_cut.py 

在 video_cut_.py 
input_video_file="E:\\testvideo\\IMG_1066.mov" 指定輸入檔

#### TODO 
1.你可以自己用click command line 執行當 或 pyqt 做一個簡單的UI
2.之後打算用 hmmlearn 實做一個比較複雜的識別器, 可以加強識別 不雅字及 環境雜音 例如,幹,啊,嗯,車子聲,關門聲,圾垃車聲,走路聲

