from datetime import datetime
from time import sleep

'''
while loop is execute 
At every second 00, of every minute, the action within the if statement is performed
'''

flag_zero_seconds = False
while True:
    now_min_secs = datetime.utcnow().strftime("%M:%S")
    now_min_secs = now_min_secs.split(":")
    if int(now_min_secs[1]) == 0 and flag_zero_seconds == False:
        print(now_min_secs, datetime.utcnow().strftime("%M:%S"))
        flag_zero_seconds = True
    elif int(now_min_secs[1]) != 0 and flag_zero_seconds == True:
        # once we passed 00secs 
        # reset flag_zero_seconds
        flag_zero_seconds = False
    sleep(1)
