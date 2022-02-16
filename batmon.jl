struct Msg
    plugout::String
    plugin::String
end
msg = Msg("Plug it out, you damned brat!", "Plug it in, you frickin moron!")

struct Commands
    plugout::Cmd
    plugin::Cmd
end
cmds = Commands(`espeak -p 70 -s 150 $(msg.plugout)`, `espeak -p 70 -s 150 $(msg.plugin)`)

struct Battery
    state::String
    power::String
end

while true
    battery_dev = read(pipeline(`upower -e`, `grep BAT`), String)[1:(end-1)]
    battery_info = read(pipeline(`upower -i $battery_dev`, `grep -E "state|perc"`), String)
    battery_info = filter.(x->x!="", split.(split(battery_info, "\n")," "))
    battery = Battery([battery_info[1][2],battery_info[2][2]]...)
    charge = parse(Int8, battery.power[1:(end-1)])

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