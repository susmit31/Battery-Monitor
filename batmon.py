import os, sys, time, threading
import pandas as pd
import pyttsx3
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
            tty.setcbreak(fd) # set non echo mode
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

def plot_data(filename):
    import matplotlib.pyplot as plt
    data = pd.read_csv(filename).tail(400)
    battery = data.battery
    memory = data.memory
    plt.figure()
    plt.plot(battery)
    plt.plot(memory)
    plt.legend(['Battery', 'Memory'])
    plt.savefig('./graphs/perf.png')

########################
# BASIC CONFIGURATIONS #
SLEEP_TIME = 2 #sleep for 2 "units"
UNIT = 60 #seconds
MSG_PLUGIN = "Plug it in, you frickin moron!" #what to yell when the battery's low
MSG_PLUGOUT = "Plug it out, you damned brat!"

os.chdir(sys.path[0]) # the first element of the path list
# is the directory where the script lives
# if the script was invoked from elsewhere,
# we'll now move into the code's directory

# Make a directory to store graphs if it's not already there 
if 'graphs' not in os.listdir():
    os.mkdir('graphs')

# Make a file to store data if it's not already there
if 'data.csv' not in os.listdir():
    data = open('data.csv', 'w')
    data.write('battery,memory')
    data.close()

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

CHECK_POW = "echo \"$(acpi | awk '{print $4}' | sed 's/%,//g') $(acpi | awk '{print $3}' | sed 's/,//g')\""
CHECK_MEM = 'free -m'
'''
An aside on redirection and piping. On UNIX, the pipe operator "prev|next" sends the output of "prev" to
the input of "next". The redirection operator "prev > file" writes the output of "prev" to "file".

In Python, {f = os.popen("command")} will pipe the output of "command" to a file object f. This is how
we can capture stdout outputs from bash within Python. 

However, for capturing stdout outputs FROM WITHIN PYTHON, i.e. outputs by print statements, here's what 
we do. Under the hood, print() is writing to the io.StringIO stream object sys.stdout, i.e.
print = sys.stdout.write + additional options. In the REPL, after the execution of each line, sys.stdout
is opened in write mode, so the previous contents cannot be retrieved. For whole scripts, the outputs
are buffered into one single stream, and then fed into sys.stdout.

If we temporarily assign a blank StringIO() object to the name sys.stdout, whenever Python calls 
sys.stdout.write, it'd be writing to our custom defined stream, not the actual standard output 
stream. At the end of capturing, we'd restore the value of sys.stdout to its original value. 
Here's the code:

old_stdout = sys.stdout
sys.stdout = StringIO()
print("Whatever")
print("Yes")
print("OK")
x = sys.stdout.getvalue()
sys.stdout = old_stdout
print(x) # prints "Whatever\nYes\nOK"

While this is how it works under the hood, we need not write this tedious stretch of code for simply
redirecting the output to a file. Here's the standard way to do it in Python. It's effectively a
shorthand for the above code block.

from contextlib import redirect_stdout
with redirect_stdout(StringIO()) as f:
    print("Whatever you want")
output = f.read()

Note that this WILL NOT work with {os.system()}, which sends the command to bash for execution, which 
handles stdout from its own context. Therefore renaming sys.stdout to a blank StringIO() doesn't help.
Therefore we have to use {os.popen()} to pipe the shell output into a file.
'''
ALERT_PLUGIN = f'espeak "{MSG_PLUGIN}"'
ALERT_PLUGOUT = f'espeak "{MSG_PLUGOUT}"'
ENGINE = pyttsx3.init()

print("Press q to quit.")

state = {'quit':False}
input_thread(await_input, state)

while True:
    # checking power
    with os.popen(CHECK_POW) as f:
        output = f.read().split(' ')
    bat_perc = int(output[0])
    
    # checking memory usage
    with os.popen(CHECK_MEM) as f:
        mem = [int(m) for m in f.readlines()[1].split()[1:]]
    mem_usg = round(100*(1 - mem[-1]/mem[0]),2)

    with open("data.csv", "a") as f:
        f.write(f"\n{bat_perc}, {mem_usg}")

    if output[1]=='Discharging\n':
        if bat_perc <= MIN_CHARGE:
            # os.system(ALERT_PLUGIN)
            ENGINE.say(MSG_PLUGIN)
            ENGINE.runAndWait()
    else:
        if bat_perc >= MAX_CHARGE:
            # os.system(ALERT_PLUGOUT)
            ENGINE.say(MSG_PLUGOUT)
            ENGINE.runAndWait()
            plot_data("data.csv")

    curr_time = time.time()
    stop_time = curr_time + SLEEP_TIME*UNIT
    while time.time() < stop_time:
        fancy_print("Watching")
