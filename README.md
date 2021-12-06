# Team 4: Picture Puzzle #
We are building a puzzle in the Ubiquitous Computing Lab (UCL) aka Escape Room in WS21/22.
The Firmware folder contains all the Software code used for this project. 
In the Sequences folder are the created sequences as .mp4 and .pdf and also a solution file.
The Hardware folder contains most of the manuals and guides for the used hardware parts in our riddle for example the pin-assignment for the ESP32.

## Content#* [Puzzle in Storyline](#1)
* [How the puzzle works](#2)
* [Project Timeline](#3)
* [Hardware](#4)

## Puzzle in Storyline <a name="1"></a>
The players face a horrible situation because a solar storm happens while they visit a power supplier. This results in shutting down all electricity which is very dangerous because we are in the year 2050 and the blind trust in the technology is so big that this shutdown could be an apocalyptic scenario.
So the group needs to get access to the lab and server room and reboot the server with the control-software. In this way they can save our city by starting the electricity. 

Our picture puzzle starts after the team got acces to the lab and server room and solved the knock knock riddle to activate the server. So the server is working now but still secured by a code. To solve this puzzle the group needs to work as a team and under time pressure.
To stop unauthorized access the code can only be solved by people who work in the lab and know the enviroment. Another security mechanism is the need of more than one person similar to the two-man-mechanism from nuclear codes. The group needs to walk around and communicate with each other to solve it in time. 
After finding the solution and tiping it into the server, they get acces and are allowed to upload the control-software. 

Accordingly the Escape Room is solved. 
  

## How the puzzle works<a name="2"></a>
The puzzle starts by showing a video sequence of picture cutouts included in a mathematical equation. The players need to find the corresponding picture from the cutout and take the number below into the equation to get one digit of the solution. There is a total of four equations with cutouts and therefore consists the solution of four digits.
After showing the four equations the sequence restarts as long as a predefined time. Afterwards there will be a completely new sequence with other cutouts in other mathematical equations. Such a equation with a given cutout can be seen in the following picture:
<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Sequences/demo-sequence.PNG">
When seeing this on the server display the players should recognize this picture cutout from the rooms they played in before. Because in the entry room and the lab room are many warning signs at the walls. An overview of all the warning signs can be seen in the next picture:
<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Sequences/warning-signs.svg">
We placed them in pairs of two pictures at different walls in different rooms so the players have to use the whole space. Additionally we force the group to communicate with each other and benefit teamwork.
Under each picture will be a seven segment display and a button. The display only shows a number when the related button is pressed. To stop one person to stand in the middle of the room and look at the numbers under each picture.
XXHier Foto von fertigem AufbauXXX
<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Sequences/demo-sign.png">

By finding the four pictures and the resulting four numbers and putting them in the equations the group should get a four digit code which they need to type in the server with a given numpad.
Overall does every picture pair consists of one ESP32, two buttons and four seven segment displays. The server consists of the numpad, Raspberry Pi and a display. All the ESP32 and the Raspberry Pi communicate via MQTT.
At the beginning all the devices are waiting for the start message. When receiving this message the Raspi will start with the first sequence and the ESP32 will power the buttons so they will light up and show the corresponding first number on the seven segment display when pressed. 
After some time has passed and the puzzle is not solved the Raspberry Pi sends a MQTT message at the enviroment group to play a text to speech: "new sequence". So the players know that sequence has changed. Also the ESP32 receive a MQTT message from the Raspi that they need to change the numbers. 
Therefore all numbers are saved in an array. 


## Project Timeline <a name="3"></a>
- [x] Concept finding for puzzle
- [x] Creating a BOM
- [x] Programming and testing OTA and MQTT with ESP32
- [x] Preparing warning signs and creating coutout sequences
- [x] First rough test run in the Escape room
- [x] Assembly of hardware for the under pictures buttons & 7-segment-displays
- [x] First software prototype for controlling the 7-segment-displays with arcade buttons
- [ ] ...
- [ ] Last testing and bug fixing
- [ ] Final run and presentation

## Hardware <a name="4"></a>
