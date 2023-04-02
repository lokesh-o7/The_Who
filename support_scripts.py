import numpy as np
import time
import os
import pandas as pd
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

MAX_WORDS = 15
def stitch_transcripts(files):
    files = [r"D:\U00726991\CEG7370_DC\discord_proj\data\user_1.txt",
             r"D:\U00726991\CEG7370_DC\discord_proj\data\user_2.txt"]
    df_all = []
    start_dt = pd.to_datetime("1-Apr-2023 12:00:00")

    # parse out each users transcript into a more useable format
    for file_i in files:
        with open(file_i, 'r') as fin:
            lines = fin.readlines()

        words, starts, ends, sent_ids = [], [], [], []
        sent_id = 0 # keep track of each sentence
        for i in np.arange(4, len(lines)):
            if ',,' in lines[i]:
                word, _, st, end = lines[i].split(',')
            else:
                word, st, end = lines[i].split(',')
            st, end = float(st), float(end)

            sent_ids.append(sent_id)
            if '.' in word: # if period is found start new sentence
                word = word.split('.')[0]
                sent_id += 1
                
            words.append(word)
            starts.append(st)
            ends.append(end)
        
        df = {'word':words, 'start':starts, 'end':ends, 'sent_id':sent_ids}
        df = pd.DataFrame(df)
        df['user'] = os.path.basename(file_i).split('.')[0]
        df_all.append(df)
    
    # sort each sentence by start time
    df_all = pd.concat(df_all, ignore_index=True)
    sent_sort = df_all.groupby(['user','sent_id'])['start'].min().reset_index()
    sent_sort = sent_sort.sort_values('start')

    # merge all sentences in order of start time
    merge_lines = []
    for loc, df_row in sent_sort.iterrows():
        user_id, sent_id = df_row[['user','sent_id']]
        get_idx = (df_all['user'] == user_id) & (df_all['sent_id'] == sent_id)
        words = df_all.loc[get_idx, 'word'].tolist()
        time_s = df_all.loc[get_idx, 'start'].iloc[0]
        timestamp = start_dt + pd.Timedelta(seconds=time_s)
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        sentence = ' '.join(words)
        sentence = "{}, {} >> {}.\n".format(user_id, timestamp, sentence)
        merge_lines.append(sentence)
    
    # write out final merged transcript
    out_dir = os.path.dirname(files[0])
    out_file = os.path.join(out_dir, 'merge_script.txt')
    with open(out_file, 'w') as fout:
        fout.writelines(merge_lines)

def run_test():
    files = [r"D:\U00726991\CEG7370_DC\discord_proj\data\ylativ.mp3",
             r"D:\U00726991\CEG7370_DC\discord_proj\data\lokesh.mp3"]

    audio_info = {}
    for file_i in files:
        basename = os.path.basename(file_i).split('.')[-1]
        clip_and_timestamp(file_i)

if __name__ == '__main__':
    stitch_transcripts(None)
    # run_test()