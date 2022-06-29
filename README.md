# polywins.py
A polywins inspired workspace AND window lister, written in Python. Heavy WIP.
BSPWM only. Requires xprop, wmctrl, xdo and slop.

<img align="right" src="https://github.com/CordlessCoder/polywins.py/raw/main/screenshot.png">

## Installing the required packages

Arch Linux:
```bash
yay -S xorg-xprop xdo wmctrl slop
```

## Adding to polybar

You need to create a module of the `custom/script` type, and with the `tail` property set to true.

#### Example:
```ini
[module/polywins]
type = custom/script
exec = ~/.config/polybar/scripts/polywins.py $MONITOR
format = <label>
label = %output%
label-padding = 0
tail = true
```

You will also need to use a script to make sure polybar runs on all montitors and knows what monitor it's on.
#### Example:
<pre lang=bash>#!/usr/bin/env bash

# Terminate already running bar instances
killall -q polybar
# If all your bars have ipc enabled, you can also use
# polybar-msg cmd quit

if type "xrandr" >/dev/null; then
	for m in $(polybar -m | cut -d':' -f1); do
		MONITOR=$m polybar --reload main_bar &
	done
else
	polybar --reload main_bar &
fi</pre>

and in your main bar:
<pre lang=ini>monitor = ${env:MONITOR:}</pre>
