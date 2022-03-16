#!/bin/bash

#
# Simple script to setup secondary monitors using xrandr
#

after_actions() {
    # redraw wallpaper
    command -v wallpaper >/dev/null && wallpaper

    # restart conky
    [ -x ~/.conky/conky-startup.sh ] && ~/.conky/conky-startup.sh &

    # hide the pidgin main window if popped up
    command -v wmctrl >/dev/null || return
    {
      sleep 0.5
      pidgin_w="$(wmctrl -l | grep "Buddy List" | tail -n 1 | cut -f1 -d " ")"
      [ $? -eq 0 ] && { sleep 2; wmctrl -ic $pidgin_w; }
    } > /dev/null 2> /dev/null
}

mirror_flag=0
dual_direction="--left-of"
process_cmdline() {
  while [ -n "$1" ]; do
    param="$(echo "$1" | sed -r "s/^(.*)=.*/\1/")"

    if [[ "$param" != "$1"  ]]; then
       _VAL=$(echo "$1" | sed -r "s/^.*=(.*)/\1/g");
       _USED_NEXT=0
    else
       _VAL="$2"
       _USED_NEXT=1
    fi

    case "$param" in
      -m|--mirror)
        mirror_flag=1
        ;;

      --below)
        dual_direction="--below"
        ;;

      --above)
        dual_direction="--above"
        ;;

      *)
      echo "Unknown option '$param'" >&2
      exit 1
      ;;
    esac
    shift
  done
}


##############################################################################
#primary_disp=$(xrandr --listmonitors | tail -n +2| grep '*' | awk '{print $4}')
#sec_disp=$(xrandr --listmonitors | tail -n +2| grep '^[[:space:]]*2:' | awk '{print $4}')
#third_disp=$(xrandr --listmonitors | tail -n +2| grep '^[[:space:]]*3:' | awk '{print $4}')

process_cmdline "$@"

# FIXME: get rid of ~/.second_disp file, use xrandr instead
# FIXME: require single_disp first when the other displays are connected..
#        ...or something...

primary_disp="eDP-1"
sec_disp=$(xrandr -q | grep "\Wconnected" | grep -v "^$primary_disp\W" -m 1 | cut -d " " -f 1);

# set second display
if [ -n "$sec_disp" ] ; then
  # TODO: check mirror
   xrandr --auto --output "$sec_disp" --mode "1920x1080" "$dual_direction" "$primary_disp"
   echo $sec_disp > ~/.second_disp
fi

# set third display
if [ -n "$sec_disp" ]; then
  third_disp=$(xrandr -q | grep "\Wconnected" | grep -vE "^($sec_disp|$primary_disp)\W" -m1 | cut -d " " -f 1);
  if [ -z "$third_disp" ]; then
     echo "No third display."
  else
    xrandr --output "$third_disp" --mode "1920x1080" --left-of "$sec_disp" --rotate right
    echo "$third_disp" >> ~/.second_disp
  fi

fi

after_actions
