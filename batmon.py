import os, sys, time, threading
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

########################
# BASIC CONFIGURATIONS #
SLEEP_TIME = 2 #sleep for 2 "units"
UNIT = 60 #seconds
MSG = "Plug it in, you frickin moron!" #what to yell when the battery's low
########################

if len(sys.argv) < 2:
    opt = input("When should we alert you?\nA. 15%\nB. 20%\nC. 25%\n(Hit Enter for default 20%)\n")
    MIN_CHARGE = 20 if opt in ['', 'b', 'B'] else (15 if opt in ['a','A'] else 25)
else:
    MIN_CHARGE = 20

CHECK_POW = 'upower -i $(upower -e | grep BAT) | grep -E "state|perc" > batmon.txt'
ALERT = f'spd-say "{MSG}"'

print("Press q to quit.")

state = {'quit':False}
input_thread(await_input, state)
while True:
    os.system(CHECK_POW)
    with open("batmon.txt") as f:
        output = f.read().split()

    if output[1]=='discharging':
        perc = int(output[3][:-1])
        if perc <= MIN_CHARGE:
            os.system(ALERT)

    curr_time = time.time()
    stop_time = curr_time + SLEEP_TIME*UNIT
    while time.time() < stop_time:
        fancy_print("Watching")