import numpy as np
import time
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import matplotlib.pyplot as plt
import pyqtgraph as pg

#pydub works in milliseconds: Frames/1000 = s, s * 1000 = Frames

def clip_and_timestamp(mp3_file):
    audio_obj = AudioSegment.from_mp3(mp3_file)

    # use mono channel to save space
    # TODO: determine if channels increase speech to text accuracy
    audio_L = audio_obj.split_to_mono()[0]

    a_parts = split_on_silence(audio_L, min_silence_len=100, silence_thresh=-45, keep_silence=50)
    new_audio = AudioSegment.empty()
    for a_p in a_parts:
        new_audio += a_p

    new_file = mp3_file.replace(".mp3", "_small.mp3")
    new_audio.export(new_file)

    # hz = audio_L.frame_rate

    # # convert raw data to array for signal processing
    # data = np.fromstring(audio_L.raw_data, dtype='int16')

    # talk_idx = (data > 100) | (data < -100)
    # pause_idx = np.where(~talk_idx)[0]
    # talk_idx = np.where(talk_idx)[0]

    # new_audio_bin = np.ndarray.tobytes(data[talk_idx])
    # kwargs = {'sample_width':audio_L.sample_width, 'frame_rate':audio_L.frame_rate, 'channels':audio_L.channels}
    # new_auio_obj = AudioSegment.from_raw(new_audio_bin, **kwargs)
    
    # stop = 1

def run_test():
    files = [r"D:\U00726991\CEG7370_DC\discord_proj\data\ylativ.mp3",
             r"D:\U00726991\CEG7370_DC\discord_proj\data\lokesh.mp3"]

    audio_info = {}
    for file_i in files:
        basename = os.path.basename(file_i).split('.')[-1]
        clip_and_timestamp(file_i)

if __name__ == '__main__':
    run_test()