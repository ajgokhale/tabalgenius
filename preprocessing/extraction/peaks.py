import wave, math
import matplotlib.pyplot as plt
import numpy as np
RMS_SAMPLE_SIZE = 441
SMOOTH_PARAM = 15
THRESHOLD = 0.7

def find_peaks(file):
    wf = wave.open(file, 'rb')
    print(wf.getframerate())
    data = convert_to_rms(wf)
    smooth_data = smooth(np.array(data), SMOOTH_PARAM)
    peaks = [i for i in range(1, len(smooth_data) - 1) 
        if smooth_data[i] - smooth_data[i-1] > 0 and smooth_data[i] - smooth_data[i+1] > 0]
    peaks = remove_redundancy(smooth_data, peaks)
    peaks_time = convert_frames_to_time(peaks, wf.getframerate())
    return peaks_time

def convert_frames_to_time(peaks, frame_rate):
    return [((peak + 0.5) * RMS_SAMPLE_SIZE) / frame_rate for peak in peaks]

def convert_to_rms(wf):
    firstByte = 0
    sample = 0
    numOfFrames = int(wf.getnframes())
    numOfSampleChunks = numOfFrames // RMS_SAMPLE_SIZE
    rmsData = []
    for sampleChunkNum in range(numOfSampleChunks):
        readFrames = wf.readframes(RMS_SAMPLE_SIZE)
        rmsData.append(calculate_rms(readFrames))
    return rmsData

def calculate_rms(frames):
    sum1 = 0.0
    for index, data in enumerate(frames):
        if index % 4 == 0:
            firstByte = data
        elif index % 4 == 1:
            sample = data*256+firstByte
            if sample > 32767:
                sample -= 65536
            sum1 += (sample**2)
    return sum1#math.log(((sum1 / RMS_SAMPLE_SIZE) ** 0.5),10)

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def remove_redundancy(data, peaks):
    neighbors = [peaks[0]]
    processed = []
    for peak in peaks:
        if peak - SMOOTH_PARAM > neighbors[-1]:
            max_val, max_index = 0, -1
            for neighbor in neighbors:
                if data[neighbor + 1] > max_val:
                    max_val = data[neighbor + 1]
                    max_index = neighbor
            processed.append(max_index) 
            neighbors = []
        neighbors.append(peak)
    return processed


### FOR TESTING ###

TEST_FILE = "../../data/raw-videos/IMG_9512.wav"
peaks = find_peaks(TEST_FILE)
print(peaks)
