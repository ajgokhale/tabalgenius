from Tkinter import *
import tkFileDialog
import pygame,time,os,string,math
from PIL import Image,ImageTk
import wave
pygame.mixer.pre_init(11025, -16, 1, 512)
pygame.mixer.init()

class bols:
#a 'bols' object can be used to interact with the recording buffer
    def __init__(self):
        self.startPos=0.
        self.endPos=0.
        self.bolType=0
        self.x1=0
        self.x2=0
    def calculateCoordinates(self,length,offset):
    #updates pixel values based on the timing of note
        self.x1=offset+int(500*(self.startPos/length))
        self.x2=offset+int(500*(self.endPos/length))

class clipPieces:
#a 'clipPieces' object can be used to interact with the master window
    def __init__(self):
        self.startPos=0.
        self.endPos=0.
        self.x1=0
        self.x2=0
        self.name=''
        self.buffer=[]
    def calculateCoordinates(self,length):
    #updates pixel values based on the timing of clip
        self.x1=int(c.d.w*(self.startPos/length))
        self.x2=int(c.d.w*(self.endPos/length))

def initKeyboard(defaultMap):
#creates a list of pygame sounds that can be accessed during recording and
#playback
    keyboardMap=[tuple()]*10
    for val in xrange(10):
        inputFileName=defaultMap[val]
        keyboardMap[val]+=\
            (pygame.mixer.Sound('tablaSounds\\'+inputFileName+'.wav'),)
        fileObject=wave.open('tablaSounds\\'+inputFileName+'.wav',
            mode='rb')
        keyboardMap[val]+=\
            (float(fileObject.getnframes())/fileObject.getframerate(),)
        fileObject.close()
    return keyboardMap

def mousePressed(event):
    root.focus()
    c.d.selectedClip=None
    if c.d.recordingBuffer!=[] and event.y<252 and event.x<c.d.w-c.d.clipsWid:
        if c.d.editModeText=='Stop Editing':
        #allows the user to select a note in the buffer
            bolNumber=(event.y-c.d.generalMargin)/c.d.heightOfBox
            for index in xrange(len(c.d.bolObjects)-1,-1,-1):
                bol=c.d.bolObjects[index]
                if bol.bolType==bolNumber and bol.x1<=event.x and\
                    bol.x2>=event.x:
                    c.d.bolEditingIndex=index
                    redrawAll()
                    return None
                c.d.bolEditingIndex=None
                redrawAll()
        else:
        #allows the user to select a beat to begin playback
            beatNumber=int((event.x-c.d.offset)/c.d.interval)
            c.d.pauseOffset=beatNumber*60/c.d.bpm
            redraw2(beatNumber)
            for index in xrange(len(c.d.recordingBuffer)):
                if c.d.recordingBuffer[index][1]>c.d.pauseOffset:
                    c.d.playbackIndex=index
                    break

def mousePressed2(event):
    root.focus()
    c.d.selectedClip=None
    drawClips()
    if c.d.editModeText=='Start Editing':
    #allows the user to select a clip in the master window
        for index in xrange(len(c.d.clipBuffer)):
            clip=c.d.clipBuffer[index]
            if clip.x1<=event.x and clip.x2>=event.x:
                c.d.clipEditingIndex=index
                drawMasterWindow()
                return None
            c.d.clipEditingIndex=None
            drawMasterWindow()

def mousePressedClips(event):
    #allows the user to select a clip in the clip window
    root.focus()
    clipNumber=(event.y-c.d.generalMargin)/20
    if clipNumber<len(c.d.savedClips) and event.y>c.d.generalMargin:
        c.d.selectedClip=clipNumber
    else:
        c.d.selectedClip=None
    drawClips()

def keyPressed(event):
    if event.char in c.d.map:
    #plays a note
        char=c.d.map[event.char]
        playSound(char)
        if c.d.recordButtonText=="Stop Recording":
            c.d.recordingBuffer+=[(char,time.time()-c.d.recordingStart)]
    elif c.d.bolEditingIndex!=None and c.d.recordingBuffer!=[] and \
        c.d.editModeText=='Stop Editing':
    #moves notes in the recording buffer
        object=c.d.bolObjects[c.d.bolEditingIndex]
        dTime=0
        change=eval(c.d.quantizeVar.get()+'.0')*60/c.d.bpm
        if event.keysym=='Right':
            dTime=change
        elif event.keysym=='Left':
            dTime=-change
        object.startPos+=dTime
        object.endPos+=dTime
        if object.startPos<0:# or object.endPos>c.d.bufferEnd:
            object.startPos-=dTime
            object.endPos-=dTime
        elif object.endPos>c.d.bufferEnd:
            c.d.bufferEnd
        object.calculateCoordinates(c.d.bufferEnd,c.d.offset)
        redrawAll()
    elif event.keysym=='Return' and c.d.selectedClip!=None:
    #adds a clip from the clip window to the master window
        addClip()
        for clip in c.d.clipBuffer[:-1]:
            clip.calculateCoordinates(c.d.masterLength)
        drawMasterWindow()
    elif c.d.clipEditingIndex!=None:
    #moves clips in the master window
        clip=c.d.clipBuffer[c.d.clipEditingIndex]
        dTime=0
        change=eval(c.d.quantizeVar.get()+'.0')*60/c.d.bpm
        if event.keysym=='Right':
            dTime=change
        elif event.keysym=='Left':
            dTime=-change
        clip.startPos+=dTime
        clip.endPos+=dTime
        if clip.startPos<0:
            clip.startPos-=dTime
            clip.endPos-=dTime
        if clip.endPos>c.d.masterLength:
            c.d.masterLength=clip.endPos*1.25
            recalculateCoordinates()
        clip.calculateCoordinates(c.d.masterLength)
        drawMasterWindow()

def recalculateCoordinates():
#recalculates the pixel coordinates of a 'bols' object
    for clip in c.d.clipBuffer:
        clip.calculateCoordinates(c.d.masterLength)

def deleteElement(event):
    if c.d.clipEditingIndex!=None:
        c.d.clipBuffer.pop(c.d.clipEditingIndex)
        c.d.clipEditingIndex=None
        drawMasterWindow()
    elif c.d.bolEditingIndex!=None:
        c.d.bolObjects.pop(c.d.bolEditingIndex)
        c.d.bolEditingIndex=None
        redrawAll()

def createBol(event):
    if c.d.editModeText=='Stop Editing' and c.d.recordingBuffer:
    #creates a new note in the recording buffer
        if event.x>c.d.offset:
            newBol=bols()
            newBol.bolType=(event.y-c.d.generalMargin)/c.d.heightOfBox
            newBol.startPos=(event.x-c.d.offset)*c.d.bufferEnd/500.0
            newBol.endPos=newBol.startPos+c.d.keyboardMap[newBol.bolType][1]
            newBol.calculateCoordinates(c.d.bufferEnd,c.d.offset)
            c.d.bolObjects+=[newBol]
            resetBuffer()
            redrawAll()

def addClip():
#adds a clip to the master window
    clip=c.d.savedClips[c.d.selectedClip]
    newClip=clipPieces()
    newClip.buffer=clip[1]
    if c.d.clipBuffer==[]:
        newClip.startPos=0
    else: 
        endTime=c.d.clipBuffer[-1].endPos
        bps=c.d.bpm/60.0
        newClip.startPos=math.ceil(endTime*bps)/bps
    newClip.endPos=newClip.startPos+clip[2]
    c.d.masterLength=newClip.endPos*1.25
    newClip.calculateCoordinates(c.d.masterLength)
    newClip.name=clip[0]
    #numOfBeats=clip[2]*c.d.bpm/60
    c.d.clipBuffer+=[newClip]

def playSound(key):
#plays a note 
    x=0
    if c.d.defaultMap[int(key)][-1]=='L':x=1
    pygame.mixer.Channel(x).play(c.d.keyboardMap[int(key)][0])

def metronomeInit():
    if c.d.metroButtonText=="Stop Metronome":
        c.d.metroButtonText="Start Metronome"
        c.d.metronomeButton.config(text=c.d.metroButtonText,bg='#82DDF0')
        c.d.metronoming=False
    else:
        c.d.metroButtonText="Stop Metronome"
        c.d.metronomeButton.config(text=c.d.metroButtonText,bg='#5BC0BE')
        c.d.metronoming=True
        c.d.metronomeDelay=60*1000/c.d.bpm # milliseconds

def recordInit():
    if c.d.recordButtonText=="Stop Recording":
        c.d.recordButtonText="Start Recording"
        c.d.recordButton.config(bg='#82DDF0')
        c.d.bufferEnd=time.time()-c.d.recordingStart
        analyzeBuffer()
        setBolObjects()
        redrawAll()
    else:
        c.d.recordingBuffer=[]
        c.d.recordButtonText="Stop Recording"
        c.d.recordButton.config(bg='#5BC0BE')
        c.d.recordingStart=time.time()
        c.d.playbackIndex=0
        c.d.pauseOffset=0
        c.d.saveButton.config(state=NORMAL)
        c.d.quantized=False
        record()

def setBolObjects():
#reinitializes the list of bols based on the recording buffer
    c.d.bolObjects=[]
    for bol in c.d.recordingBuffer:
        newBol=bols()
        newBol.startPos=bol[1]
        newBol.endPos=newBol.startPos+(c.d.keyboardMap[int(bol[0])][1])
        newBol.bolType=int(bol[0])
        newBol.calculateCoordinates(c.d.bufferEnd,c.d.offset)
        c.d.bolObjects+=[newBol]

def editInit():
    if c.d.editModeText=='Start Editing':
        c.d.editModeText='Stop Editing'
        c.d.quantizeButton.config(state=NORMAL)
        c.d.editButton.config(bg='#5BC0BE')
        changeStateButtons(DISABLED)
        c.d.clipEditingIndex=None
        redrawAll()
    else:
        c.d.editModeText='Start Editing' 
        c.d.quantizeButton.config(state=DISABLED)
        c.d.editButton.config(bg='#82DDF0')
        c.d.bolEditingIndex=None
        c.d.bolObjects.sort(key=sortBolObjects)
        resetBuffer()
        c.d.playbackIndex=0
        c.d.pauseOffset=0
        #indexing got screwed up when rearranging bols, need to normalize
        changeStateButtons(NORMAL)
        redrawAll()

def changeStateButtons(state):
#either disables or activates a button based on mode
    c.d.recordButton.config(state=state)
    c.d.saveButton.config(state=state)
    c.d.playbackButton.config(state=state)
    c.d.metronomeButton.config(state=state)
    c.d.readButton.config(state=state)

def sortBolObjects(x):
#sorting key for 'bols' objects
    return x.startPos

def resetBuffer():
#reinitializes the recording buffer based on the 'bols' objects
    c.d.recordingBuffer=[]
    for bol in c.d.bolObjects:
        c.d.recordingBuffer+=[(str(bol.bolType),bol.startPos)]

def playbackBuffer():
#initializes the playback of the recording buffer
    if c.d.playbackButtonText=="Pause":
        c.d.playbackButtonText="Play"
        c.d.playbackButton.config(image=c.d.playIcon)
    else:
        c.d.playbackButtonText="Pause"
        c.d.playbackButton.config(image=c.d.pauseIcon)
        c.d.playbackStart=time.time()
        c.d.savedPlaybackIndex=c.d.playbackIndex
        play(c.d.recordingBuffer,False)        

def playbackMaster():
#plays the master window
    c.d.clipPlaybackFinished=True
    c.d.masterPlaybackStart=time.time()
    playbackLoop(0)

def playbackLoop(clipPlaybackIndex):
#cycles through the clip buffer for playback
    if clipPlaybackIndex<len(c.d.clipBuffer):
        if c.d.clipPlaybackFinished and \
            c.d.clipBuffer[clipPlaybackIndex].startPos<time.time()-\
            c.d.masterPlaybackStart:
            c.d.clipPlaybackFinished=False
            c.d.playbackStart=time.time()
            c.d.playbackIndex=0
            play(c.d.clipBuffer[clipPlaybackIndex].buffer,True)
            clipPlaybackIndex+=1
        c.after(1,playbackLoop,clipPlaybackIndex)

def analyzeBuffer():
#analyzes the recording buffer
#NOTE: NOT YET IMPLEMENTED
    if len(c.d.recordingBuffer)>1 and c.d.recordButtonText=="Start Recording":
        separated=separatePhrases()
        if separated:
            separated=[0]+separated+[len(c.d.recordingBuffer)]
            phrases=[]
            for index in xrange(len(separated)-1):
                phrases+=[[]]
                for val in c.d.recordingBuffer\
                    [separated[index]:separated[index+1]]:
                    phrases[-1]+=[val[0]]
        separated=separatePhrasesBeat()

def separatePhrases():
#separates the recording buffer based on spacing
    differences=[]
    for bufferIndex in xrange(1,len(c.d.recordingBuffer)):
        differences+=[c.d.recordingBuffer[bufferIndex][1]-
            c.d.recordingBuffer[bufferIndex-1][1]]
    sum1=sum(differences)
    avg=sum1/len(differences)
    squareSum=0
    for val in differences:
        squareSum+=(avg-val)**2
    standardDev=squareSum/len(differences)
    separatedIndices=[]
    #print 'here'
    if standardDev*30>avg:
        #print 'there'
        for index in xrange(len(differences)):
            if differences[index]-avg>standardDev:
                separatedIndices+=[index+1]
    return separatedIndices

def separatePhrasesBeat():
#separates the recording buffer based on beat
    separatedIndices,index=[],0
    bps=c.d.bpm/60.0
    for beat in xrange(1,int(math.ceil(c.d.bufferEnd*bps))+1):
        separatedIndices+=[[]]
        while index<len(c.d.recordingBuffer) and\
            c.d.recordingBuffer[index][1]*bps<beat:
            separatedIndices[-1]+=c.d.recordingBuffer[index][0]
            index+=1
    return separatedIndices

def saveBuffer():
    if c.d.recordingBuffer!=[] and c.d.recordButtonText=="Start Recording":
        clipName = c.d.audioNameEntry.get()
        c.d.audioNameEntry.delete(0,END)
        if len(clipName)==0:
            clipName='Clip'+str(len(c.d.savedClips))
        clipName=''.join(clipName.split())
        c.d.savedClips+=[(clipName,c.d.recordingBuffer,c.d.bufferEnd)]
        drawClips()
        c.d.saveButton.config(state=DISABLED)

def openSavedBuffer(event):
#load a clip into the recording buffer
    if c.d.selectedClip!=None:
        clip=c.d.savedClips[c.d.selectedClip]
        c.d.recordingBuffer=clip[1]
        setBolObjects()
        redrawAll()

def quantizeBuffer(buffer,master):
    if buffer!=[] and c.d.recordButtonText=="Start Recording" and \
        c.d.editModeText=="Stop Editing":
        if master:spacing=(1/8.0)*60/c.d.bpm
        else:spacing=eval(c.d.quantizeVar.get()+'.0')*60/c.d.bpm
        for index in xrange(len(buffer)):
            bol=buffer[index]
            buffer[index]=\
                (bol[0],round(bol[1]/spacing)*spacing)
        checkForRepeats(buffer)
        if not master:
            setBolObjects()
            redrawAll()
            c.d.quantized=True

def checkForRepeats(buffer):
#removes any repeats in the recording buffer
    previousTime,allBols=0,[False]*10
    index=0
    while index<len(buffer):
        type=int(buffer[index][0])
        if buffer[index][1]==previousTime:
            if allBols[type]==True:
                buffer.pop(index)
            else:
                allBols[type]=True
                index+=1
        else:
            previousTime=buffer[index][1]
            allBols=[False]*10
            index+=1

def play(buffer,master):
    playbackStart=c.d.playbackStart
    index=c.d.playbackIndex
    leniency=0.1
    #initializing common local variables
    currentTime=time.time()-playbackStart+c.d.pauseOffset
    if c.d.playbackButtonText=="Play" and not master:
        c.d.pauseOffset+=time.time()-playbackStart
    #checks if playback has been paused
    elif c.d.playbackIndex<len(buffer) and \
        currentTime<=buffer[-1][1]+leniency:
        if currentTime>buffer[index][1]:# and not c.d.playbackRepeatCheck:
            #checks if the current time falls within range of the next sound
            playSound(buffer[index][0])
            c.d.playbackIndex+=1
        if c.d.metronoming and not master:
            playClick(currentTime,'play')
        c.after(1, play,buffer,master)
    elif not master:
        c.d.playbackIndex=c.d.savedPlaybackIndex
        playbackBuffer()
    else:
        c.d.clipPlaybackFinished=True

def record():
    recordingStart=c.d.recordingStart
    currentTime=time.time()-recordingStart
    if c.d.recordButtonText=="Start Recording":
        return None
    #checks if recording has been stopped
    elif c.d.metronoming:
        playClick(currentTime,'record')
    c.after(1, record)

def playClick(currentTime,state):
#plays a metronome click
    bps=c.d.bpm/60.0
    rounded=round(currentTime/bps)
    if c.d.metroTimePrevious<=round(c.d.metroTimePrevious) and\
        currentTime*bps>round(currentTime*bps):
        metroSound=pygame.mixer.Sound(c.d.metroFile)
        pygame.mixer.Channel(c.d.metroChannel).play(metroSound)
        if state=='play':
            redraw2(rounded)
    c.d.metroTimePrevious=currentTime*bps

def notateComposition():
    if c.d.clipBuffer!=[]:
        for clip in c.d.clipBuffer:
            for bol in clip.buffer:
                c.d.notateBuffer+=[bol]
                c.d.notateBuffer[-1]=(c.d.notateBuffer[-1][0],\
                    c.d.notateBuffer[-1][1]+clip.startPos)
        quantizeBuffer(c.d.notateBuffer,True)
        createNotationFile()

def createNotationFile():
    bps=c.d.bpm/60
    notateBufferIndex=0
    currentBeat=1
    checkFolder()
    filename=getFile()
    notated=open('SavedFiles\\'+filename+'.txt','w+')
    lengthOfComp=math.ceil(c.d.notateBuffer[-1][1]*bps)
    if lengthOfComp%1==0: lengthOfComp+=1
    for cycleNum in xrange(int(math.ceil(lengthOfComp/len(c.d.taal)))):
        for sectionNum in xrange(len(c.d.notationCode)):
            notated.write(c.d.notationCode[sectionNum][1]+'\n')
            line=''
            for beatNum in xrange(c.d.notationCode[sectionNum][0]):
                previousBol=currentBeat-(1/8.0)
                bolBeat=''
                while notateBufferIndex<len(c.d.notateBuffer) and \
                    c.d.notateBuffer[notateBufferIndex][1]*bps<currentBeat:
                    beatFraction=c.d.notateBuffer[notateBufferIndex][1]*bps
                    if beatFraction==previousBol:pass
                    else:
                        bolBeat+='-   '*(int(round((beatFraction-
                            previousBol)*8))-1)
                        splitName=c.d.defaultMap[int(c.d.notateBuffer\
                            [notateBufferIndex][0])].split('-')
                        bolName=splitName[0]
                        if splitName[1]!='L' and splitName[1]!='R':
                            bolName+='*'    
                        bolBeat+=bolName+' '*(4-len(bolName))
                        previousBol=beatFraction
                    notateBufferIndex+=1
                line+='| '+bolBeat+'-   '*(8-len(bolBeat)/4)
                currentBeat+=1;
            notated.write(line+'\n')
    notated.close()

def readNotatedFile():
    bps=c.d.bpm/60.0
    filename=''
    filename=tkFileDialog.askopenfilename()
    if filename[-4:]=='.txt':
        length=0
        clipName=filename.split('/')[-1]
        notatedFile=open(filename)
        newBuffer=[]
        line=notatedFile.readline()
        line=notatedFile.readline()[:-1]
        fullClip=[]
        while line:
            notations=[]
            beats=line.split('|')[1:]
            for beat in beats:
                length+=1
                beat=beat[1:]
                for index in xrange(len(beat)/4):
                    notations+=[beat[index*4:(index+1)*4]]
            for index in xrange(len(notations)):
                if notations[index][0]!='-':
                    char =c.d.reverseDict[notations[index].rstrip()]
                    startTime=index*(1/8.0)/bps 
                    newBuffer+=[(char,startTime)]   
            line=notatedFile.readline()
            line=notatedFile.readline()[:-1]
        c.d.savedClips+=[(clipName,newBuffer,length/bps)]
    redrawAll()    

def checkFolder():
    if not os.path.exists('SavedFiles'):
        os.mkdir('SavedFiles')

def getFile():
    filename=c.d.fileNameEntry.get()
    c.d.fileNameEntry.delete(0,END)
    if filename=='':
        filename='Composition'+str(len(os.listdir('SavedFiles')))
    return filename

def drawRect(position): #for metronome
    x=c.d.offset+position*c.d.interval
    c.create_rectangle(x,0,x+c.d.interval,c.d.h,width=0,fill='#5bc0be')

def drawBar(position): #for metronome
    x=c.d.offset+position*c.d.interval
    c.create_line(x,0,x,10*c.d.heightOfBox+10,width=3)

def drawClips():
    clips.create_rectangle(0,0,c.d.clipsWid,c.d.h,fill='#3a506b')
    clips.create_line(0,0,0,c.d.h,fill='white')
    for index in xrange(len(c.d.savedClips)):
        boxColor='#3a506b';textColor='white'
        if index==c.d.selectedClip:
            boxColor='#82ddf0';textColor='#1c2541'
        clips.create_rectangle(1,index*20,c.d.clipsWid,
            (index+1)*20,fill=boxColor,width=0)
        clips.create_text(c.d.clipsWid/2,9+index*20,text=c.d.savedClips[index][0],
            fill=textColor,anchor=CENTER)
    c.create_line(0,0,c.d.w,0,fill='black')

def drawMasterWindow():
    heightOfBox=c.d.heightOfBox
    c2.create_rectangle(0,0,c.d.w,c.d.h2,fill='white')
    c2.create_rectangle(0,c.d.h2-(c.d.h-(10*heightOfBox+10)),
        c.d.w,c.d.h2,width=0,fill='#3a506b')
    c2.create_rectangle(0,0,c.d.w,c.d.generalMargin,width=0,fill='#3a506b')
    c2.create_line(0,0,c.d.w,0,fill='white')
    if c.d.clipBuffer!=[]:
        length=c.d.masterLength
        numOfBeats=(c.d.bpm/60.0)*length
        c.d.interval2=interval2=c.d.w/numOfBeats
        for beatNumber in xrange(1,int(numOfBeats)+1):
            c2.create_line(int(interval2*beatNumber),
                0,int(interval2*beatNumber),10,fill='white')
        for clipIndex in xrange(len(c.d.clipBuffer)):
            clip=c.d.clipBuffer[clipIndex]
            color='#5bc0be'
            if clipIndex==c.d.clipEditingIndex: color='#3a506b'
            c2.create_rectangle(clip.x1+2,heightOfBox+2,
                clip.x2+2,heightOfBox*3+2,fill='black',width=0)
            c2.create_rectangle(clip.x1,heightOfBox,
                clip.x2,heightOfBox*3,fill=color,width=0)
            c2.create_text((clip.x1+clip.x2)/2,heightOfBox*2,text=clip.name,
                anchor=CENTER,fill='black',font='20')

def redrawAll(background=True):
    if background: c.create_rectangle(0,0,c.d.w,c.d.h,fill='white')
    heightOfBox=c.d.heightOfBox
    for index in xrange(10):
        c.create_rectangle(0,c.d.generalMargin+index*heightOfBox,100,
            (index+1)*heightOfBox+10,fill='black',width=0)
        c.create_text(95,heightOfBox+index*heightOfBox,
            text=c.d.defaultMap[index][:-2],fill='white',anchor=E)
    c.create_rectangle(0,0,c.d.w-c.d.clipsWid,c.d.generalMargin,
        width=0,fill='#3a506b')
    c.create_rectangle(0,10*heightOfBox+10,
        c.d.w-c.d.clipsWid,c.d.h,width=0,fill='#3a506b')
    if c.d.recordingBuffer!=[]:
        length=(c.d.bufferEnd)
        numOfBeats=(c.d.bpm/60.0)*length
        c.d.interval=interval=500.0/numOfBeats
        for beatNumber in xrange(0,int(numOfBeats)+1):
            c.create_line(100+int(interval*beatNumber),
                0,100+int(interval*beatNumber),10,fill='white')
        for bolIndex in xrange(len(c.d.bolObjects)):
            bol=c.d.bolObjects[bolIndex]
            color='#82ddf0'
            if bolIndex==c.d.bolEditingIndex: color='#3a506b'
            c.create_rectangle(bol.x1+2,
                c.d.generalMargin+bol.bolType*heightOfBox+2,
                bol.x2+2,(bol.bolType+1)*heightOfBox+10+2,fill='black',width=0)
            c.create_rectangle(bol.x1,
                c.d.generalMargin+bol.bolType*heightOfBox,
                bol.x2,(bol.bolType+1)*heightOfBox+10,fill=color,width=0)
            c.create_line(bol.x1,c.d.generalMargin+bol.bolType*heightOfBox,
                bol.x1,(bol.bolType+1)*heightOfBox+10)
    drawClips()
    drawMasterWindow()

def redraw2(position):
    c.create_rectangle(0,0,c.d.w,c.d.h,fill='white')
    drawRect(position)
    drawBar(position)
    redrawAll(False)
    drawClips()

def init(wid,hei):
    c.d.w=wid;c.d.h=hei;c.d.width=35
    c.d.recordState=NORMAL
    c.d.recordButtonText="Start Recording";c.d.playbackButtonText="Play"
    c.d.recordingBuffer=[];c.d.recordingStart=0
    c.d.playbackIndex=0;c.d.savedPlaybackIndex=0
    c.d.playbackStart=0;c.d.pauseOffset=0
    c.d.bufferEnd=0
    c.d.playbackRepeatCheck=False
    c.d.savedClips=[]

    c.d.generalMargin=11;c.d.buttonBorder=2

    c.d.bpm=60
    c.d.metronomeStart=0;c.d.metroState=NORMAL
    c.d.metroButtonText="Start Metronome";c.d.metroTimePrevious=0
    c.d.metronomeDelay=-1;c.d.metroChannel=2
    c.d.metroFile='Metronome2.wav';c.d.metronoming=False

    c.d.interval=0;c.d.interval2=0
    c.d.offset=100;c.d.heightOfBox=24

    c.d.selectedClip=None;c.d.clipBuffer=[];c.d.masterLength=0
    c.d.clipEditingIndex=None;c.d.copiedClip=None

    c.d.editModeText='Start Editing'
    c.d.bolObjects=[];c.d.bolEditingIndex=None
    c.d.quantized=False;c.d.notateBuffer=[]

    c.d.taal=['dha','dhin','dhin','dha',
        'dha','dhin','dhin','dha',
        'na','tin','tin','ta',
        'ta','dhin','dhin','dha']
    c.d.notationCode=[(4,'X'),(4,'1'),(4,'O'),(4,'2')]

    initImages()
    
    c.d.defaultMap=defaultMap=['ghe-L','ke-L','te-R','re-R',
    'te-middlefinger-R','dhe-R','na-open-R','na-sharp-R','tun-R','ghe-2-L']
    createReverse(defaultMap)
    c.d.map={'e':'9','w':'9','2':'1','p':'2','l':'3',
    '[':'4',';':'5',',':'6','.':'7','\'':'8','s':'0','d':'0'}
    c.d.keyboardMap=initKeyboard(defaultMap)

def createReverse(map):
    reverseDict=dict()
    for index in xrange(len(map)):
        splitBol=map[index].split('-')
        name=splitBol[0]
        if splitBol[1]!='L' and splitBol[1]!='R':
            name+='*'
        reverseDict[name]=str(index)
    c.d.reverseDict=reverseDict

def initImages():
    c.d.metronomeIcon=imageHelper('Metronome')
    c.d.recordIcon=imageHelper('Record')
    c.d.playIcon=imageHelper('Play');c.d.pauseIcon=imageHelper('Pause')
    c.d.saveIcon=imageHelper('Save');c.d.editIcon=imageHelper('Edit')
    c.d.quantizeIcon=imageHelper('Quantize')
    c.d.notateIcon=imageHelper('Notate')
    c.d.readIcon=imageHelper('Read')

def imageHelper(fileName):
    image=Image.open('Icons\\'+fileName+'.png')
    image=image.resize((35,35),Image.ANTIALIAS)
    return ImageTk.PhotoImage(image)

def defineButton(image,command):
    return Button(root, image=image, #text =text, 
        command = command,relief=FLAT,bd=c.d.buttonBorder,
        bg="#82DDF0",width=c.d.width,height=c.d.width)

def defineButtons():
    c.d.metronomeButton=defineButton(c.d.metronomeIcon,metronomeInit)
    c.d.recordButton=defineButton(c.d.recordIcon,recordInit)
    c.d.playbackButton=defineButton(c.d.playIcon,playbackBuffer)
    c.d.playbackMasterButton=defineButton(c.d.playIcon,playbackMaster)
    c.d.editButton=defineButton(c.d.editIcon,editInit)
    c.d.saveButton=defineButton(c.d.saveIcon,saveBuffer)
    c.d.quantizeButton=defineButton(c.d.quantizeIcon,
        lambda:quantizeBuffer(c.d.recordingBuffer,False))
    c.d.notateButton=defineButton(c.d.notateIcon,notateComposition)
    c.d.readButton=defineButton(c.d.readIcon,readNotatedFile)
    c.d.quantizeButton.config(state=DISABLED)

def placeButtons():
    width=c.d.width
    defineButtons()

    buttonOffset=25    
    c.d.quantizeVar=StringVar(root)
    c.d.quantizeVar.set('1/16')
    c.d.quantizeMenu=OptionMenu(root,c.d.quantizeVar,
        '1/2','1/4','1/8','1/16','1/32','1/64')
    c.d.quantizeMenu.place(x=(width+10)*6,y=c.d.h-buttonOffset,anchor=W,
        width=(width)*2+15)
    c.d.quantizeMenu.config(relief=FLAT,bg="#82DDF0",bd=0,
        highlightthickness=0)
    
    c.d.audioNameEntry=Entry(root,width=15)
    c.d.fileNameEntry=Entry(root,width=15)

    c.d.metronomeButton.place(x=0,y=c.d.h-buttonOffset,anchor=W)
    c.d.recordButton.place(x=(width+10),y=c.d.h-buttonOffset,anchor=W)
    c.d.playbackButton.place(x=(width+10)*2,y=c.d.h-buttonOffset,anchor=W)
    c.d.editButton.place(x=(width+10)*3,y=c.d.h-buttonOffset,anchor=W)
    c.d.quantizeButton.place(x=(width+10)*4,y=c.d.h-buttonOffset,anchor=W)
    c.d.readButton.place(x=(width+10)*5,y=c.d.h-buttonOffset,anchor=W)
    c.d.saveButton.place(x=(width+10)*8,y=c.d.h-buttonOffset,anchor=W)
    c.d.audioNameEntry.place(x=(width+10)*9,y=c.d.h-buttonOffset,anchor=W)

    c.d.playbackMasterButton.place(x=0,y=c.d.h+c.d.h2-buttonOffset,anchor=W)
    c.d.notateButton.place(x=(width+10),y=c.d.h+c.d.h2-buttonOffset,anchor=W)
    c.d.fileNameEntry.place(x=(width+10)*2,y=c.d.h+c.d.h2-buttonOffset,anchor=W)

    c.d.playbackMasterButton.place()

def run():
    global c,c2,clips,root
    root = Tk()
    wid=725;hei=300
    c=Canvas(root, width=wid, height=hei,bd=0,relief=FLAT,highlightthickness=0)
    class Struct: pass
    c.d = Struct()
    c.d.clipsWid=clipsWid=wid-600;c.d.h2=hei2=150
    clips= Canvas(root,width=clipsWid,height=hei,bd=0,
        relief=FLAT,highlightthickness=0)
    c2=Canvas(root,width=wid,height=hei2,bd=0,relief=FLAT,highlightthickness=0)
    init(wid,hei)
    c.bind("<Button-1>", mousePressed);c.bind("<Double-Button-1>", createBol)
    c2.bind("<Button-1>", mousePressed2)
    clips.bind("<Button-1>", mousePressedClips)
    clips.bind("<Double-Button-1>", openSavedBuffer)
    root.bind("<Key>", keyPressed);root.bind("<Key-Delete>", deleteElement)
    c.pack();c2.pack();clips.place(x=wid-clipsWid,y=0,anchor=NW)
    redrawAll();placeButtons()
    root.iconbitmap('Icons\\MainIcon.ico');root.wm_title('Tabalgenius')
    root.mainloop()  
run() 
