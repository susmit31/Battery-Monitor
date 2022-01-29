# BAT-MON
A really tiny battery monitoring script to help out my dumb Linux Mint battery monitor which only _displays_ an alert when the battery's low. Of course, a visual notification requires you to be in front of the laptop in the first place. If you're not exactly in front of the laptop and it runs outta charge, it'll just silently shut itself off. And then there's the issue of _overcharging_: I'll plug it in and completely forget about the fact that it's been charging for, say, 4 hours. In this case, there's _no notifications_ at all. So that's another problem.

So I wrote this small script that uses the Linux package _speech-dispatcher_ to yell at you when the battery goes below a certain limit, or if it's being charged, when the charge goes _above_ a certain limit. 