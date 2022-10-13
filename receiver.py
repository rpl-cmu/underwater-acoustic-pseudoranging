import math
from datetime import datetime
import time
import wave
import pyaudio
import numpy as np
import soundfile as sf
import os

form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 48000  # 48kHz sampling rate
chunk = 512  # 2^12 samples for buffer
record_secs = 2  # seconds to record
dev_index = 4  # device index found by p.get_device_info_by_index(ii)
fldr_name = datetime.now().isoformat(timespec='minutes')
txt_name = fldr_name + "/results.txt"
os.mkdir(fldr_name)

audio = pyaudio.PyAudio()  # create pyaudio instantiation

# create pyaudio stream
stream = audio.open(format=form_1, rate=samp_rate, channels=chans,
                    input_device_index=dev_index, input=True,
                    frames_per_buffer=chunk)



def goertzel(samples, sample_rate, *freqs):
    """
    Goertzel algorithm implementation. Used for detecting individual frequencies in a discrete fourier series. 
    'samples' is a windowed one-dimensional signal originally sampled at 'sample_rate'.
    The function returns 2 arrays as follows: first being the actual frequenies, and then the coefficients as '(real part, imag part, power)'.
    Power is good enough for detection purposes. 

    ***Not used as matched filtering is more effective.*** 

    """
    window_size = len(samples)
    f_step = sample_rate / float(window_size)
    f_step_normalized = 1.0 / window_size

    # Calculate all the DFT bins we have to compute to include frequencies
    # in `freqs`.
    bins = set()
    for f_range in freqs:
        f_start, f_end = f_range
        k_start = int(math.floor(f_start / f_step))
        k_end = int(math.ceil(f_end / f_step))

        if k_end > window_size - 1:
            raise ValueError('frequency out of range %s' % k_end)
        bins = bins.union(range(k_start, k_end))

    # For all the bins, calculate the DFT term
    n_range = range(0, window_size)
    freqs = []
    results = []
    for k in bins:

        # Bin frequency and coefficients for the computation
        f = k * f_step_normalized
        w_real = 2.0 * math.cos(2.0 * math.pi * f)
        w_imag = math.sin(2.0 * math.pi * f)

        # Doing the calculation on the whole sample
        d1, d2 = 0.0, 0.0
        for n in n_range:
            y = samples[n] + w_real * d1 - d2
            d2, d1 = d1, y

        # Storing results `(real part, imag part, power)`
        results.append((
            0.5 * w_real * d1 - d2, w_imag * d1,
            d2**2 + d1**2 - w_real * d1 * d2)
        )
        freqs.append(f * sample_rate)
    return freqs, results

# define sound collection function


def recorder(name):

    """
    Function to recored audio periodically as defined by main.
    """

    stream.start_stream()
    # print("start recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0, int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)

    # print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()

    wavefile = wave.open(name, 'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()



def compute_dist(dist1, dist2, D2 = False):
    """"
    Euclidean distance computation
    """
    if D2:
        dist = dist = np.sqrt((dist1[0] - dist2[0])**2 + (dist1[1] - dist2[1])**2)
    else:
        dist = np.sqrt((dist1[0] - dist2[0])**2 + (dist1[1] - dist2[1])**2 + (dist1[2] - dist2[2])**2)
    return dist



def compute_pos(pseudo_ranges_obs, beac_pos, rec_pos_est, bias_guess):
    """
    Backend optimization for pseudorange estimation
    """

    b = []
    A = []
    
    for i in range(4):
        R_i = compute_dist(beac_pos[i,:],rec_pos_est)
        b.append(pseudo_ranges_obs[i] - R_i - bias_guess*1480)
        A.append([(rec_pos_est[0] - beac_pos[i,0])/R_i, (rec_pos_est[1] - beac_pos[i,1])/R_i, (rec_pos_est[2] - beac_pos[i,2])/R_i, 1480])
    
    A = np.asarray(A)
    b = np.asarray(b)
    sigma = np.identity(4)
    sigma = np.array(([0.01, 0, 0, 0], [0, 0.01, 0, 0], [0, 0, 0.01, 0] ,[0, 0, 0, 0.01]))
    sqtinf = np.linalg.inv(sigma)**0.5
    
    A = sqtinf@A
    b = sqtinf@b
    AtAinv = np.linalg.inv(np.matmul(A.T, A))


    delta_xyzt = np.matmul(AtAinv, np.matmul(A.T,b))
    return delta_xyzt, A, b




def pseudorange(timings, rec_pose_init):
    """
    Function to estimate position of receiver given beacon position
    """
    sound_speed = 1480
    bias_guess = 1.0
    pseudo_ranges_obs = timings
    pseudo_ranges_obs = np.asarray(pseudo_ranges_obs)*sound_speed
   
    rec_pos_est = rec_pose_init
    res = [100, 100, 100, 1]
    b1_xyz = [-2.42, -2.42, 2.1376]
    b2_xyz = [-2.42,2.42 , 2.0]
    b3_xyz = [2.42, 2.420, 0.20144]
    b4_xyz = [3.42, 0, 1.5494]
    beac_pos = [b1_xyz, b2_xyz, b3_xyz, b4_xyz]

    beac_pos = np.asarray(beac_pos)
    count =  0

    while (np.abs(res[0])>0.01 and np.abs(res[1])>0.01 and np.abs(res[2])>0.01 and count<4):
        delta_xyzt, A,b = compute_pos(pseudo_ranges_obs, beac_pos, rec_pos_est, bias_guess); 
        res = delta_xyzt[0:4] 
        rrec_pos_est = rec_pos_est + delta_xyzt[0:3].T
        bias_guess = bias_guess + res[3]
        count +=1
        gdop = np.sqrt(np.trace(np.linalg.inv(np.matmul(A.T,A))))
        if gdop > 1000:
            break # likely to get optimizer stuck if gdop is high
    return rec_pos_est

def NormalizeData(data):
    """
    0-1 normalization of matched filter output
    """
    return (data - np.min(data)) / (np.max(data) - np.min(data))


def reader(temp_name, txt_name,template1):

    """
    Function to read recorded wav files and start position estimation
    """
    #print("trying to read wavfile")
    data, samplerate = sf.read(temp_name, dtype='float32')
    #matched filter and get sample numbers of sequence
    r1 = np.abs(np.correlate(template1,data,mode='full')[len(template1)-1:])[::-1] 
    r1 = NormalizeData(r1)

    i = 0
    samples = []
    count = 1
    while i<r1.size:
        if r1[i]>0.12:
            # print('t'+ str(count)+'=' + str(i-9600*(count-1)))
            count = count+1
            samples.append(i)
            i = i+9000 # Original chirps are 9600 samples apart
        else:
            i = i + 1


    timings = [samples[0]/48000,samples[1]/48000,samples[2]/48000,samples[3]/48000]  
    rec_pose_init = [1.5, 1.5, 1.5]

    rec_pose_new = pseudorange(timings,rec_pose_init)

    print(rec_pose_new)
    #print("finished pseudorange")
    with codecs.open(txt_name, "a", "utf-8") as my_file:  
        my_file.write(str(rec_pose_new) + "\n")
    rec_pose_init = rec_pose_new


def main():
    
    template1, sr = sf.read('templates/10ms_template.wav', dtype='float32')
    # template2, sr = sf.read('templates/temp2qd.wav', dtype='float32')
    # template3, sr = sf.read('templates/temp3q.wav', dtype='float32')
    # template4, sr = sf.read('templates/temp4qd.wav', dtype='float32')
    

    count = 0
    flag = False
    try:
        while True:
            t = datetime.now().strftime('%S')
            if (t[1] == '9' and flag == False):
                temp_name = fldr_name + "/test_" + str(count) + ".wav"
                count = count + 1
                recorder(temp_name)
                print(t)
                flag = True
               # time.sleep(0.2)
                reader(temp_name, txt_name,template1)
                

            elif (t[1] != '9'):
                flag = False

    except KeyboardInterrupt:
        stream.close()
        audio.terminate()


if __name__ == "__main__":
    main()
# start stream of audio data
