# Team 4: Picture Puzzle #
We are building a puzzle in the Ubiquitous Computing Lab (UCL) aka Escape Room in WS21/22.
The Firmware folder contains all the Software code used for this project. 
In the Sequences folder are the created sequences as .mp4 and .pdf and also a solution file.
The Hardware folder contains most of the manuals and guides for the used hardware parts in our riddle for example the pin-assignment for the ESP32.

## Content #
* [Puzzle in Storyline](#1)
* [How the puzzle works](#2)
* [MQTT Documentation](#3)
* [Hardware](#4)
* [Project Timeline](#5)


## Puzzle in Storyline <a name="1"></a>
The players face a horrible situation because a solar storm happens while they visit a power supplier. This results in shutting down all electricity which is very dangerous because we are in the year 2050 and the blind trust in the technology is so big that this shutdown could be an apocalyptic scenario.
So the group needs to get access to the lab and server room and reboot the server with the control-software. In this way they can save our city by starting the electricity. 

Our picture puzzle starts after the team got acces to the lab and server room and solved the knock knock riddle to activate the server. So the server is working now but still secured by a code. To solve this puzzle the group needs to work as a team and under time pressure.
To stop unauthorized access the code can only be solved by people who work in the lab and know the enviroment. Another security mechanism is the need of more than one person similar to the two-man-mechanism from nuclear codes. One person always needs to stand at the server and press a button there while the others can walk freely in the room. The group needs to walk around and communicate with each other to solve it in time. 
After finding the solution and typing it into the server, they get access and the server reboots which results in saving our world. 

Accordingly the Escape Room is solved. 
  

## How the puzzle works<a name="2"></a>
The puzzle starts by showing a text that the red button on the server needs to be pressed the whole time. After that a video sequence of picture cutouts included in a mathematical equation is shown. Simultanously there starts a text-to-speach which says that the server is locked and a password needs to be entered. The players need to find the corresponding picture from the cutout and take the number below into the equation to get one digit of the solution. There is a total of four equations with cutouts and therefore consists the solution of four digits.
After showing the four equations the sequence restarts as long as a predefined time. This predefined time depends on the amount of players. Two players get more time than four. Afterwards there will be a completely new sequence with other cutouts in other mathematical equations. Such a equation with a given cutout can be seen in the following picture:
<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Firmware/Raspberry/sequences/0_0.jpg">
When seeing this on the server display the players should recognize this picture cutout from the rooms they played in before. Because in the entrance room and the lab room are many warning signs at the walls. An overview of all the warning signs can be seen in the next picture:
<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Sequences/warning-signs.svg">
We placed them in pairs of two pictures at different walls in different rooms so the players have to use the whole space. Additionally we force the group to communicate with each other and benefit teamwork.
Under each picture will be a seven segment display and a button. The display only shows a number when the related button is pressed. To stop one person to stand in the middle of the room and look at the numbers under each picture. This can be seen in the next picture:
<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Hardware/esp.jpeg">

By finding the four pictures and the resulting four numbers and putting them in the equations the group should get a four digit code which they need to type in the server with a given numpad.
Overall does every picture pair consists of one ESP32, two buttons and four seven segment displays. The server consists of the numpad, Raspberry Pi and a display. Additionally there is an ESP32 with a seven-segment-display which represents the timer and a red button. The numpad, timer and red button can be seen in the next picture:

<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Hardware/server.jpeg" height="500">


All the ESP32 and the Raspberry Pi communicate via MQTT. Further MQTT informations can be found in the [MQTT Documentation](#3) or the [MQTT overview](https://github.com/ubilab-ws21/puzzle-4/tree/main/MQTT "MQTT overview").
At the beginning the Raspberry Pi is sending a retained message to the operator and AR hint system. After that it is waiting for the start message from the operator. When receiving this message the Raspi will send the starting sequence to the ESPs and starts with the first sequence. The ESP32 will power the buttons so they will light up and show the corresponding first number on the seven segment display when pressed. 
After some time has passed and the puzzle is not solved or the players enter a wrong code or the red button on the server dropped the Raspberry Pi sends a MQTT message at the text to speech to play a text to speech: "new sequence". So the players know that sequence has changed. Also the ESP32 receive a MQTT message from the Raspi that they need to change the numbers, a new sequence is shown on the display and the timer restarts. 
Therefore all numbers are saved in an array. 

The following flow chart shows the overall course of events of our puzzle.
<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Sequences/puzzle-ablaufplan.png">

## MQTT Documentation <a name="3"></a>
In our communication design we distinguish between internal and external communication. The Raspi does everything external with the operator and hint system. The Raspi is sending and receiving informations from and to the individual ESPs. So all ESPs communicate internally with each other. A better overview for our MQTT communication and structure can be seen in the MQTT folder. There are also tables with the used topics and messages. 
[MQTT overview](https://github.com/ubilab-ws21/puzzle-4/tree/main/MQTT "MQTT overview")

## Hardware <a name="4"></a>
All documents and manuals needed to reconstruct this puzzle are in the "Hardware" folder.
The following picture gives on overview how the used hardware inside of the created case looks like:

<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Hardware/open_case.jpeg" height="500">


## Project Timeline <a name="5"></a>
- [x] Concept finding for puzzle
- [x] Creating a BOM
- [x] Programming and testing OTA and MQTT with ESP32
- [x] Preparing warning signs and creating cutout sequences
- [x] First rough test run in the Escape room
- [x] Assembly of hardware for the under pictures buttons & 7-segment-displays
- [x] First software prototype for controlling the 7-segment-displays with arcade buttons
- [x] Soldering all parts together
- [x] Designing a 3D case in SolidWorks
- [x] Assembly of electronic with first case
- [x] Creating the GUI and Software for the Raspberry
- [x] Edit the 3D case and print the missing parts
- [x] Conception and creation of the timer 
- [x] Testing the network communication between the systems in the escape room
- [x] Assembly of the missing parts
- [x] Designing the final sequences for the riddle
- [x] Printing and foil-coating the pictures
- [x] Mount all parts in the room
- [x] Added progress bar after finishing the riddle
- [x] Implement extra button as dead-man switch
- [x] Fixed issues after integration run
- [x] Make use of AR hint system
- [x] Coordinate MQTT with operator
- [x] Provide power supply for all of them
- [x] Last testing and bug fixing
- [x] Finish documentation
- [x] Final run
- [x] very last bug fixes
- [x] Final run 2.0

