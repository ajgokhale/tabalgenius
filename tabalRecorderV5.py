import pyaudio
import wave, math
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"
RMS_SAMPLE_SIZE = 882
slopeThreshold = 0.7

p = pyaudio.PyAudio()

def record(fileName,audio):
    wf = wave.open(fileName, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(audio))
    wf.close()

def mean(numbers):
    avg = math.fsum(numbers)/(max(len(numbers),1))
    return avg

def halfValue(numbers):
    half = (max(numbers)+min(numbers))/2
    return half

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()
record(WAVE_OUTPUT_FILENAME,frames)
wf = wave.open(WAVE_OUTPUT_FILENAME,'rb')
readFrames = wf.readframes(100)
firstByte = 0
sample = 0
numOfFrames = int(wf.getnframes())
numOfSampleChunks = numOfFrames/RMS_SAMPLE_SIZE
print 'The frame is '+str(numOfFrames)
wf.rewind()
rmsData = []
for sampleChunkNum in xrange(numOfSampleChunks):
    readFrames = wf.readframes(RMS_SAMPLE_SIZE)
    sum1 = 0.0
    for index,data in enumerate(readFrames):
        if index%4==0:
            firstByte = int(data.encode('hex'), 16)
        elif index%4==1:
            sample = int(data.encode('hex'), 16)*256+firstByte
            if sample > 32767:
                sample -= 65536
            sum1+=(sample**2)
    rms = math.log(((sum1/RMS_SAMPLE_SIZE)**0.5),10)
    rmsData.append(rms)
for val in rmsData:
    print val
deriv = 0
totalIncrement = totalDecrement = startIncreasePoint = peakVolume = \
    peakIndex = beginIncreaseIndex = 0
findPeakIndex = 1
decreasing = True
peaks = []
averageVolume = mean(rmsData)
halfVolume = halfValue(rmsData)
print "The average is "+str(averageVolume)
print "The half is "+str(halfVolume)
for index in xrange(1,len(rmsData)-1):
    deriv = rmsData[index]-rmsData[index-1]
    if deriv > 0:
        if decreasing:
            decreasing = False
            beginIncreaseIndex = index-1
            totalDecrement = 0
            totalIncrement = 0
            startIncreasePoint = rmsData[index-1]
            print str(startIncreasePoint)
        if rmsData[index]>peakVolume:
            peakVolume = rmsData[index]
            peakIndex = index
        totalIncrement += deriv
    else:
        totalDecrement -= deriv
    if not decreasing and totalDecrement > (0.5*totalIncrement):
        decreasing = True
        print "The peak is "+str(peakVolume)
        if peakVolume > halfVolume and (peakVolume-startIncreasePoint)/(peakIndex-beginIncreaseIndex) > slopeThreshold:
            print "The slope is ",(peakVolume-startIncreasePoint)/(peakIndex-beginIncreaseIndex)
            print peakIndex-beginIncreaseIndex
            peaks.append(peakIndex)
        peakVolume = 0
        totalIncrement = 0
print peaks
        
