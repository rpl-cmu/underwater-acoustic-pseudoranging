from datetime import datetime
import time
import soundcard as sc
from scipy.io import wavfile
import numpy as np

import wave

import librosa
data2, sr = librosa.load("/home/pi/temp1q.wav", sr = 48000, mono=True, res_type='kaiser_best')


# get a list of all speakers:
speakers = sc.all_speakers()
print(speakers)

s = sc.get_speaker("CM106")
default= sc.default_speaker()
# get the current default speaker on your system:
print(s)
print(default)

flag = False

while True: 
    t = datetime.now().strftime('%S')
    
    if (t[0]=='0' and flag == False):
        flag = True
        s.play(data2, sr, channels= [1,2,3,4], blocksize=256)
        # sd.play(data, fs)
        # status = sd.wait()
        # play_obj = wave_obj.play()
        # play_obj.wait_done()  # Wait until sound has finished playing
        print(t)

    elif (t[1]!= '0'):
        flag = False

