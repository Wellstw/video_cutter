import collections
import contextlib
import sys
import wave
import datetime
import pysrt

import webrtcvad 
#if you use winpython please use this way to install webrtcvad
# click "WinPython Command Prompt.exe" under winpython folder

#python -m pip install webrtcvad-wheels

class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration
        self.is_speech=False
        
def read_wave(path):
    """Reads a .wav file.

    Takes the path, and returns (PCM audio data, sample rate).
    """
    mapdata={8000:10,
             16000:20,
             32000:30,
             48000:40
             }
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        vad_duration=mapdata.get(sample_rate)
        return pcm_data, sample_rate,vad_duration


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.

    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)



 
def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.

    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.

    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n
        
def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.

    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.

    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.

    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.

    Arguments:

    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).

    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    timestamp_st=None
    timestamp_ed=None
    results=[]
    fx=lambda x :round(x,3)
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        #sys.stdout.write('1' if is_speech else '0')
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                timestamp_st=ring_buffer[0][0].timestamp
                timestamp_st=fx(timestamp_st)
                timestamp_ed=-10.0
                print(f"+{timestamp_st}")
                #sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                timestamp_ed=frame.timestamp + frame.duration
                timestamp_ed=fx(timestamp_ed)
                results.append([timestamp_st,timestamp_ed])
                print(f"st:{timestamp_st} ed:{timestamp_ed}")
                triggered = False
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        timestamp_ed=frame.timestamp + frame.duration
        timestamp_ed=fx(timestamp_ed)
        results.append([timestamp_st,timestamp_ed])
        print(f"st:{timestamp_st} ed:{timestamp_ed}")

    return results
def speech_detect(inpfile="",srtout="",vad_mode=1,vad_speed="middle"):
    """
    description:speech detect to srt
    
    """
    fxtimesrt=lambda x:pysrt.SubRipTime.from_time((datetime.datetime.min+datetime.timedelta(seconds=float(x))).time())
    speech_type={"slow":600,
                "middle":300,
                "fast":200,
                "ultrafast":100,
                }
    srtfile = pysrt.SubRipFile()
    audio, sample_rate,vad_duration = read_wave(inpfile)
    vad = webrtcvad.Vad(vad_mode)
    
    frames = frame_generator(vad_duration, audio, sample_rate)
    frames = list(frames)
    _speed=speech_type.get(vad_speed,300)
    segments = vad_collector(sample_rate, vad_duration, _speed, vad, frames)
    print(segments)
    print("---------------------")
    merged=False
    max_merged_delta_time=_speed/1000
    merged_st=0.0
    merged_ed=0.0
    total_len=len(segments)
    idx=0
    fxtimestr=lambda x:str(datetime.timedelta(seconds=x))
    for item1,item2 in zip(segments[:-1],segments[1:]):
        #print(f"{item1},{item2} \n")
        _item_delta_time=item2[0]-item1[1]

        if (_item_delta_time<=max_merged_delta_time) and (merged is False):
            merged_st=fxtimesrt(item1[0])
            #print(f"st--{item1},{item2} \n")
            merged=True
            continue
        if (_item_delta_time>max_merged_delta_time) and (merged ):
            merged_ed=fxtimesrt(item1[1])
            print(f"Merge {idx}:{merged_st}-->{merged_ed} [speech]")
            sub = pysrt.SubRipItem(idx, start=merged_st, end=merged_ed, text="[SPEECH]")
            srtfile.append(sub)
            idx+=1
            merged=False
            merged_st=""
            merged_ed=""

    if merged:
        merged_ed=fxtimesrt(item1[1])
        sub = pysrt.SubRipItem(idx, start=merged_st, end=merged_ed, text="[SPEECH]")
        srtfile.append(sub)
        print(f"Merge {idx} :{merged_st}-->{merged_ed} [speech]")
    srtfile.save(srtout)
def main4():
    input_wav_file="E:\\testvideo\\IMG_1066.wav"
    ouput_srt_file="E:\\testvideo\\tmp.srt"   
    speech_detect(inpfile=input_wav_file,srtout=ouput_srt_file)
    

if __name__ == '__main__':
    #main2()
    #main3()
    main4()
    #main(sys.argv[1:])
