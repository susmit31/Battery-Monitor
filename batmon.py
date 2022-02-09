import os, sys, time, threading
import matplotlib.pyplot as plt
from colorain import move_cursor

def fancy_print(text):
    N_DOTS = 4
    textlen = len(text)
    _ = sys.stdout.write(text)
    print()
    move_cursor(-1,textlen)
    for i in range(N_DOTS):
        time.sleep(.5)
        _ = sys.stdout.write(".")
        print()
        move_cursor(-1,textlen+i+1)
    move_cursor(0, -textlen-N_DOTS)
    sys.stdout.write(" "*(N_DOTS+textlen))
    move_cursor(0,-textlen-N_DOTS)

def getChar():
    try:
        # for Windows-based systems
        import msvcrt # If successful, we are on Windows
        return msvcrt.getch()

    except ImportError:
        # for POSIX-based systems (with termios & tty support)
        import tty, termios  # raises ImportError if unsupported

        fd = sys.stdin.fileno()
        oldSettings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            answer = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

        return answer

def await_input(state_dict):
    while 1:
        pressed = getChar()
        if pressed == 'q':
            state_dict['quit'] = True
            os._exit(os.EX_OK)

def input_thread(handler, state_dict):
    inp = threading.Thread(target=handler, args= (state_dict,))
    inp.start()

def retrieve_and_rewrite(filename):
    # Retrieve the contents of the file, remove the trailing comma, and add a newline
    with open(filename, "r") as f:
        contents = f.read()[:-1]
        f.seek(0)
        lastline = f.readlines()[-1][:-1].split(",")
        lastline = [int(k) for k in lastline]
        plt.plot(lastline)
        plt.show()
        contents+='\n'
    with open(filename, "w") as f:
        f.write(contents)

########################
# BASIC CONFIGURATIONS #
SLEEP_TIME = 2 #sleep for 2 "units"
UNIT = 60 #seconds
MSG_PLUGIN = "Plug it in, you frickin moron!" #what to yell when the battery's low
MSG_PLUGOUT = "Plug it out, you damned brat!"
########################

if len(sys.argv) < 2:
    opt = input("When should we alert you?\nA. 15%\nB. 20%\nC. 25%\n(Hit Enter for default 20%)\n")
    MIN_CHARGE = 20 if opt in ['', 'b', 'B'] else (15 if opt in ['a','A'] else 25)
else:
    MIN_CHARGE = int(sys.argv[1])

if len(sys.argv) > 2:
    MAX_CHARGE = int(sys.argv[2])
else:
    MAX_CHARGE = 80

CHECK_POW = 'upower -i $(upower -e | grep BAT) | grep -E "state|perc" > batmon.txt'
ALERT_PLUGIN = f'spd-say "{MSG_PLUGIN}"'
ALERT_PLUGOUT = f'spd-say "{MSG_PLUGOUT}"'

print("Press q to quit.")

state = {'quit':False}
input_thread(await_input, state)
while True:
    os.system(CHECK_POW)
    with open("batmon.txt") as f:
        output = f.read().split()
    perc = int(output[3][:-1])
    with open("data.csv", "a") as f:
        f.write(f"{perc},")

    if output[1]=='discharging':
        if perc <= MIN_CHARGE:
            os.system(ALERT_PLUGIN)
            retrieve_and_rewrite("data.csv")
    else:
        if perc >= MAX_CHARGE:
            os.system(ALERT_PLUGOUT)
            retrieve_and_rewrite("data.csv")

    curr_time = time.time()
    stop_time = curr_time + SLEEP_TIME*UNIT
    while time.time() < stop_time:
        fancy_print("Watching")