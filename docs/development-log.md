# 2023.02.09

* factory reset parsivel `echo -en "CS/F/1\n" > /dev/ttyUSB0`
* print config `echo -en "CS/L\r" > /dev/ttyUSB0`
* reset parsivel `echo -en "CS/Z/1\r" > /dev/ttyUSB0`
* adjust time `echo -en "CS/T/13:12:00\r" > /dev/ttyUSB0`
* adjust date `echo -en "CS/D/01.01.2000\r" > /dev/ttyUSB0`
* read date `echo -en "CS/U\r" > /dev/ttyUSB0` 
    * `09.02.2023 12:12:09` (UTC)

* reset with [reset_parsivel.py](reset_parsivel.py)

* pyserial miniterm `python -m serial.tools.miniterm /dev/ttyUSB0 19200`

```
-----------------------------------------------------------------------                                 
PARSIVEL 2 CONFIGURATION LIST
-----------------------------------------------------------------------                                 Sensor Date And Time 09.02.2023 -14:00:23
-----------------------------------------------------------------------                                 RS485 Interface Config
-----------------------------------------------------------------------                                 RS485 Baudrate        : 19200
RS485 Bus Mode        : 0 [0 = OFF,1 =ON]
RS485 Bus Address     : 0 
-----------------------------------------------------------------------
SDI12 Interface Config
-----------------------------------------------------------------------
SDI12 Bus Mode        : 0 [0 = OFF,1 = ON]
RS485 Bus Address     : 0 
-----------------------------------------------------------------------
SDI12 Interface Config
-----------------------------------------------------------------------
SDI12 Bus Mode        : 0 [0 = OFF,1 = ON]
SDI12 Bus Address     : 0 
-----------------------------------------------------------------------
User Telegram Config
-----------------------------------------------------------------------
User Telegram mode    : 1 [0 = OFF,1 = ON]
User @mschleiss 

The Parsivel field02 measures the a Rain amount accumulated (mm). 
It's value can be reset back to 0, when the parsivel is receives a reset command?
Do you think that makes sense to reset it? It would not be too hard to do it every day at 23:59:50.Telegram String  : F01:%01;F02:%02;F03:%03;F04:%04;F05:%05;F06:%06;F07:%07;F08:%08;F09:%09;F10:%10;F11:%11;F12:%12;F13:%13;F14:%14;F15:%15;F16:%16;F17:%17;F18:%18;F20:%20;F21:%21;F22:%22;F23:%23;F24:%24;F25:%25;F26:%26;F27:%27;F28:%28;F30:%30;F31:%31;F32:%32;F33:%33;
-----------------------------------------------------------------------
Sensor Heating Config
-----------------------------------------------------------------------
Sensor Heating mode   : 1 
Temperature Threshold : +10 
-----------------------------------------------------------------------
Impulse Mode Config
-----------------------------------------------------------------------
Impulse Mode          : 0 
Poll Mode             : 1 [0 = OFF,1 = ON]
Interval time         : 60 
OK
```

config seems to be corrrect, although there is no field 61. why?

I do not know if the telegram mode should be ON or OFF: will keep it on `CS/*/D/1\r`

user telegram: `echo -en "CS/M/M/1\r" > /dev/ttyUSB0` 

telegram format: `echo -en "CS/M/S/%01;%02;\r\n" > /dev/ttyUSB0` is not changing the `User Telegram String  : CS/L`



Restart sensor, reset the rain amount: `echo -en "CS/Z/1\r" > /dev/ttyUSB0`

User telegram: `echo -en 'CS/M/M/1\r\n' > /dev/ttyUSB0 `

format telegram: `echo -en 'CS/M/S/%01;%02;%03;%04;%05;%06;%07;%08;%09;%10;%11;%12;%13;%14;%15;%16;%17;%18;%20;%21;%22;%23;%24;%25;%26;%27;%28;%30;%31;%32;%33;%34;%35;%60;%90;%91;%93;%61\r\n' > /dev/ttyUSB0`

format telegram: `echo -en 'CS/M/S/%01|%02|%03|%04|%05|%06|%07|%08|%09|%10|%11|%12|%13|%14|%15|%16|%17|%18|%20|%21|%22|%23|%24|%25|%26|%27|%28|%30|%31|%32|%33|%34|%35|%60|%90|%91|%93|%61\r\n' > /dev/ttyUSB0`



there seems to be a maximum length for the telegram format string 

poll data: `echo -en 'CS/P\r' > /dev/ttyUSB0`

print config: `echo -en "CS/L\r\n" > /dev/ttyUSB0`



## F61 only 1 value pair from each call
2023.02.16

The @mschleiss 

The Parsivel field02 measures the a Rain amount accumulated (mm). 
It's value can be reset back to 0, when the parsivel is receives a reset command?
Do you think that makes sense to reset it? It would not be too hard to do it every day at 23:59:50.F61 in te correct version is only receiving one line"

I am not sure the request is returning only 1 value, or whether the processing of the telegram is discarding the following lines.

The value capture is `'00.798;02.139\r'`

Resulting in the CSV:

```
2023-02-16T09:35:00.366139;00.785;02.381
2023-02-16T09:39:00.305705;00.517;01.347
2023@mschleiss 

The Parsivel field02 measures the a Rain amount accumulated (mm). 
It's value can be reset back to 0, when the parsivel is receives a reset command?
Do you think that makes sense to reset it? It would not be too hard to do it every day at 23:59:50.-02-16T09:48:00.884114;00.689;01.971
```

I will stop the script and send a telegram request just for F61

 `echo -en 'CS/M/S/%61\r\n' > /dev/ttyUSB0`

`echo -en 'CS/P\r\n' > /dev/ttyUSB0`

could it be that the line breaks influence it

slowing while loop to every 10min, so that the droplets can be accumulated


## debugging telegram_lines to capture all F61 values

[b'OK\r\n', b'\n', b'SVFS:0000.000;0000.00;00;00;   NP;   C;-9.999;20000;00059;12773;00000;012;450994;2.11.6;2.11.1;0.50;24.3;0;14:09:59;16.02.2023;;;0000.00;000;025;013;013;00.000;0000.0;0000.00;-9.99;0000.00;0000.00;00000007;\n', b'F90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\n', b'F91:00.000;00.000;00.000;00.000;00.000;\n', b'F93:000;000;000;000;000;000;\n', b'F61:00.502;00.853\r\n', b'00.606;02.026\r\n', b'00.550;01.595\r\n', b'00.521;01.237\r\n', b'00.540;01.070\r\n', b'00.559;01.710\r\n', b'00.571;01.572\r\n', b';']


look at regex 
