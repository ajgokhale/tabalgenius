LIBRARIES TO IMPORT:

PIL
pygame


HOW TO USE TABALGENIUS:

1. Do not change the size of the window
2. The keyboard is initialized with a default layout. 
This layout can be viewed under the "Keyboard Map" section.
3. The program contains two main windows.
The recording buffer window (top half of the screen) and the master window (bottom half).
The user can record and save clips in the recording buffer window.
These clips can then be added to the master window to be pieced together and saved.


KEYBOARD MAP:

'2'     - ke
'W'/'E' - ghe
'S'/'D' - ghe
','     - na
'.'     - na
'L'     - te
'P'     - re
'''     - tun
'['     - ti
';'     - dhe


TOP TOOLBAR (in order of appearance):

'Metronome'    - if this button is activated, the metronome will play when recording or playing back the buffer

'Record'       - if this button is activated, all sounds that are played will be added to a recording buffer, which can be played back
                 if the button is deactivated, the recording buffer will be displayed graphically

'Play/Pause'   - this button will begin to play the recording buffer from the selected beat or from where it has been paused

'Edit'         - if this button is activated, all non-editing buttons will be disabled, and the user will be in editing mode

'Quantize'     - this button can only be used in editing mode
                 this button will quantize the recording buffer based on the interval selected in the interval menu

'Read'         - this button will allow you to select a formatted text file and will convert it into a sound clip that can be added to the master window

'Interval Menu'- this menu allows the user to select the beat interval 

'Save'         - this button will save the recording buffer as a clip that can be added to the master window


BOTTOM TOOLBAR (in order of appearance):

'Play'         - this button will play the master composition

'Notate'       - this button will notate the master composition and save it as a formatted text file


EDITING:

The user can edit the recording buffer in several ways
1. A note displayed in the buffer can be selected by clicking on it
2. Once selected, a note can be moved with the right and left arrow keys based on the selected interval
3. Once selected, a note can be deleted by pressing the 'delete' button
4. A note can be added by double clicking within the window

MISCELLANEOUS:

1. Once a clip has been selected from the clip window, press the 'Enter' button to add it to the master window