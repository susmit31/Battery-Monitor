using PyPlot, DataFrames, CSV

struct Msg
    plugout::String
    plugin::String
end
msg = Msg("Plug it out, you damned brat!", "Plug it in, you frickin moron!")

struct Commands
    plugout::Cmd
    plugin::Cmd
    battery::Cmd
    memory::Cmd
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
    memusg = usedmem / totalmem

    if battery.state == "discharging"
        if charge <= 20
            run(cmds.plugin)
        end
    else
        if charge >= 80
            run(cmds.plugout)
        end
    end
    sleep(120)
end