import os, time

MINUTE = 60

MIN_CHARGE = 20

CHECK_POW = 'upower -i $(upower -e | grep BAT) | grep -E "state|perc" > batmon.txt'
ALERT = 'spd-say "Plug In... Plug In... Plug In"'

while True:
    os.system(CHECK_POW)
    with open("batmon.txt") as f:
        output = f.read().split()

    if output[1]=='discharging':
        perc = int(output[3][:-1])
        if perc < MIN_CHARGE:
            os.system(ALERT)
    
    time.sleep(5*MINUTE)