#!/bin/bash

#
# Deactivate secondary displays activated by dual_disp
#

if [[ ! -e ~/.second_disp ]]; then exit 0; fi
while read -r line; do
  [ -z "$line" ] && continue
  [ "$line" == "eDP-1" ] && {
    echo >&2 "Error: embedded display used"
    exit 1
  }
  xrandr --output "$line" --off
done < ~/.second_disp

[ -x ~/.conky/conky-startup.sh ] && ~/.conky/conky-startup.sh &
rm ~/.second_disp

command -v wmctrl >/dev/null || exit 0
{
  sleep 0.5
  pidgin_w="$(wmctrl -l | grep "Buddy List" | tail -n 1 | cut -f1 -d " ")"
  [ $? -eq 0 ] && { sleep 2; wmctrl -ic "$pidgin_w"; }
} > /dev/null 2> /dev/null

exit 0
