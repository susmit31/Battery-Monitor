# BAT-MON
A really tiny battery monitoring script to help out my dumb Linux Mint battery monitor which only _displays_ an alert when the battery's low. Even when it's locked, if it runs outta charge, it'll just silently shut itself off. Which has become really inconvenient because I often study keeping important stuff opened that I'll need to look at from time to time. Hence, I wrote this small script that uses the Linux package _speech-dispatcher_ to yell at you when the battery goes below a certain limit. 