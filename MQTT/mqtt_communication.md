| Topic | Description | Payload | Reset-Value | Subscriber | Publisher |
| :--:	| :---------: | :------:| :---------: |:--------: | :--------:|
| 3/gamecontrol| Control the radio: which puzzle state is currently in play | Enum(Gamecontrol) | idle | radio, operator | radio, operator | 
| 3/antenna/orientation | gives information if the angle of the antenna correct | boolean | false | operator | radio |
| 3/map/knob1 | gives information whether knob1 is in correct position | boolean | false | operator | radio |
| 3/map/knob2 | gives information whether knob2 is in correct position | boolean | false | operator | radio |
| 3/map/knob3 | gives information whether knob3 is in correct position | boolean | false | operator | radio |
| 3/touchgame/trialCount | gives information about the trails the group already had | int | 0 | operator | radio |
| 3/touchgame/displayTime | the game can either be set in easy or hard mode | boolean | false | radio | operator |
<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/Sequences/puzzle-ablaufplan.png">