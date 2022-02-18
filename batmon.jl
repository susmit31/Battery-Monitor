# Imports
using PyPlot, DataFrames, CSV

# Defining useful structs
struct Msg
    plugout::String
    plugin::String
end
msg = Msg("Plug it out, you damned brat!", "Plug it in, you frickin moron!")

struct Commands
    plugout::Union{Cmd, Base.OrCmds}
    plugin::Union{Cmd, Base.OrCmds}
    battery::Union{Cmd, Base.OrCmds}
    memory::Union{Cmd, Base.OrCmds}
end
cmds = Commands(
    `espeak -p 70 -s 150 $(msg.plugout)`, 
    `espeak -p 70 -s 150 $(msg.plugin)`,
    pipeline(`upower -e`, `grep BAT`),
    `free -m`
)

struct Battery
    state::String
    power::String
end

# Defining plotting function
function plot_data(fname::String)
    # Load data
    data = DataFrame(CSV.File("./$fname"))

    if length(data.battery) < 400
        plt.plot(data.battery)
        plt.plot(data.memory)
    else
        plt.plot(data.battery[end-400:end])
        plt.plot(data.battery[end-400:end])
    end
    plt.savefig("./graphs/perf-jl.png")
    plt.close()
end

while true
    # Getting battery info
    battery_dev = read(cmds.battery, String)[1:(end-1)]
    battery_info = read(pipeline(`upower -i $battery_dev`, `grep -E "state|perc"`), String)
    battery_info = filter.(x->x!="", split.(split(battery_info, "\n")," "))
    battery = Battery([battery_info[1][2],battery_info[2][2]]...)
    charge = parse(Int8, battery.power[1:(end-1)])

    # Getting memory info
    meminfo = read(cmds.memory, String) # gets the command output as a string
    meminfo = strip(meminfo) # strips the string of leading and trailing whitespaces
    meminfo = split(meminfo, "\n")[2] # splits the strings into lines keeping the one line we need
    meminfo = split(meminfo, " ") # splitting the line by whitespace
    meminfo = filter(x->x!="", meminfo)[2:end] # getting rid of empty strings made by the split
    totalmem = parse(Int16, meminfo[1])
    freemem = parse(Int16, meminfo[end])
    usedmem = totalmem - freemem
    memusg = round(100 * usedmem / totalmem, digits=2) # getting the memory usage percentage

    # Writing / appending the data to a csv
    fname = "data-jl.csv"
    # If doesn't already exist, prepare the file
    if !(fname in readdir("."))
        data = open(fname, "w")
        write(data, "battery,memory\n")
        close(data)
    end
    # Append the data to the file
    data = open(fname,"a")
    write(data, "$charge,$memusg\n")
    close(data)

    # Notification squad
    if battery.state == "discharging"
        if charge <= 20
            run(cmds.plugin)
        end
    else
        if charge >= 60
            run(cmds.plugout)
            plot_data(fname)
        end
    end

    # Repeat after 2 minutes
    sleep(120)
end