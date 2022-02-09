const fs = require('fs');
const {exec} = require('child_process');

// BASIC CONFIG
const INTVL = 2; // check the charge every INTVL units
const UNIT = 60; // 1 unit = 60 seconds
const MSG = {
    PLUGIN: "Plug it in, you frickin moron!",
    PLUGOUT: "Plug it out, you damned brat!"
};

let CHARGE_LIM;
// Parsing command line args
if (process.argv.length < 4){
    console.log("Please enter the thresholds for alerting along with the programme's name.");
    process.exit();
} else {
    CHARGE_LIM = process.argv.slice(2).map(x=>parseInt(x));
}

// Commands to execute in a shell
const CHECK_POW = "upower -i $(upower -e | grep BAT) | grep -E \"state|perc\" > batmonjs.txt";
const ALERT = {
    PLUGIN: `espeak "${MSG.PLUGIN}"`,
    PLUGOUT: `espeak "${MSG.PLUGOUT}"`
};

// Core functionality
const run_checks = ()=>{
    exec(CHECK_POW, (err, out, inp) => {
        fs.readFile('/home/shanks-mint/Desktop/projects/py/bat-mon/batmonjs.txt', 'utf8', (err, dat)=>{
            let battery_state = dat.split(' ').filter(x => x.length > 0);
            let perc = parseInt(battery_state[3].slice(0,-2));
            let discharging = battery_state[1] == 'discharging\n';
            if ( perc <= CHARGE_LIM[0] ){
                if ( discharging ) {
                    exec(ALERT.PLUGIN, (err, out, inp)=>{});
                }
            } else if ( perc >= CHARGE_LIM[1] ){
                if ( !discharging ) {
                    exec(ALERT.PLUGOUT, (err, out, inp)=>{});
                }
            }
        });
    });

}

run_checks();
setInterval(run_checks, INTVL*UNIT*1000);