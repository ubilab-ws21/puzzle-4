### MQTT topics
| Topic | Description | Subscriber | Publisher |
| :--:	| :---------: | :--------: | :--------:|
| 4/gamecontrol | general communication | operator, Raspi | operator, Raspi |
| op/gamecontrol | for the player amount | Raspi | operator |
| puzzle4/esp | messages for all 5 ESPs | ESP1-4 + Timer | Raspi |
| puzzle4/esp/timer | messages for Timer ESP | Timer ESP | Raspi |
| puzzle4/esp/timer/players | messages for Timer ESP | Timer ESP | Raspi |
| puzzle4/esp/sequence | messages for picture ESPs | ESP1-4 | Raspi |
| game/puzzle4 | AR hint system | Raspi, AR System | Raspi, AR System |

### MQTT commands
The following messages can be used to start or stop puzzle 4. These are send from the operator to the Raspi in "4/gamecontrol":
| method  | state  | data    |   | description                                                                                         |
|---------|--------|---------|---|-----------------------------------------------------------------------------------------------------|
| trigger | on     |         |   | Starts the puzzle.                                          |
| trigger | off    |         |   | Restarts the puzzle and waits for a new 'trigger on'.                         |
| trigger | off    | skipped |   | Puzzle switches immediately into the solved state and waits for a 'trigger off' to restart. |                                                   


The following messages are sent by the Raspi in "4/gamecontrol" to report the current status:

| method | state    | data |   | description                                                                         |
|--------|----------|------|---|-------------------------------------------------------------------------------------|
| status | inactive |      |   | The Raspi has finished it's initialization and waits for a 'trigger on'.            |
| status | active   |      |   | The Raspi has received a 'trigger on' message and starts the puzzle.                |
| status | solved   |      |   | The picture puzzle is solved and waits for a 'trigger off'. |

### Chart of our MQTT communication
<img src="https://github.com/ubilab-ws21/puzzle-4/blob/main/MQTT/mqtt.svg">
