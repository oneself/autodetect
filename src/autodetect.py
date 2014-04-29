#!/usr/bin/env python

import os
import re
import time
from optparse import OptionParser
from collections import namedtuple
import ConfigParser


VERBOSE = False
PRETEND = False
RESET   = False
FORCE   = False


#########
# UTILS #
#########

#BG_IMAGE = '/space/themes/wallpapers/Bamboo01-1.png'
#BG_IMAGE = '/space/themes/wallpapers/darkside-ws.png'
#BG_IMAGE = '/space/themes/wallpapers/ice.jpg'
#BG_IMAGE = '/space/themes/wallpapers/mountain-valley.jpg'
#BG_IMAGE = '/space/themes/wallpapers/Koekohe_Beach_Moeraki_South_Island_New_Zealand.jpg'
#BG_IMAGE = '/space/themes/wallpapers/awesome_orange_ws.jpg'
#BG_IMAGE = '/space/themes/wallpapers/dark_side_of_spotify.png'
#BG_IMAGE = '/space/themes/wallpapers/291716-frederika.jpg'
#BG_IMAGE = '/space/themes/wallpapers/siamese_dream.png'
BG_IMAGE = '/space/themes/wallpapers/old_school-wallpaper-1920x1080.jpg'

TRACKBALL = 'Kensington Expert Mouse Trackball'

CONNECTED_PATTERN = re.compile(r'([A-Z0-9]+) (connected|connected primary)')
RESOLUTION_PATTERN = re.compile(r'\s+(\d+)x\d+.*\+', re.MULTILINE)

Screen = namedtuple('Screen', 'name width')

def cl(command, ro=False):
  if VERBOSE:
    print '$', command
  if ro:
    return [line for line in os.popen(command)]
  elif not PRETEND:
    os.popen(command)

def get_screens():
  '''Get all screen names'''
  screens = []
  screen_name = None
  for line in cl('xrandr', True):
    resolution_matcher = RESOLUTION_PATTERN.match(line)
    if screen_name and resolution_matcher:
      screens.append(Screen(name=screen_name, width=int(resolution_matcher.group(1))))
      screen_name = None
    else:
      connected_matcher = CONNECTED_PATTERN.match(line)
      if connected_matcher:
        screen_name = connected_matcher.group(1)
  print 'Active screens: %s' % ', '.join([s.name for s in screens])
  return screens

def is_trackball():
  '''Are we using a trackball?'''
  for line in cl('lsusb', True):
    if TRACKBALL in line:
      print 'Found trackball'
      return True
  print 'Found trackpad'
  return False

def lid_state():
  lid = None
  state = cl('cat /proc/acpi/button/lid/LID/state', True)
  lid = 'open' in state
  if lid:
    print 'Lid is OPEN'
  else:
    print 'Lid is CLOSED'
  return lid

def remove_screen(screens, name):
  filter(lambda s: s.name != name, screens)

##############
# COMPONENTS #
##############

def xrandr(screens, lid):
  #cl('xrandr --output "VGA1" --rotation left --auto --output "DP2" --left-of "VGA1" --auto --rotation normal')
  if lid:
    state = 'auto'
  else:
    state = 'off'
  xrandr = ['xrandr --output %s --%s' % (screens[0].name, state)]
  if len(screens) == 2:
    xrandr.append('--output %s --left-of %s --auto' % (screens[1].name, screens[0].name))
  elif len(screens) > 2:
    xrandr.append('--output VGA1 --rotation left --auto --output %s --left-of %s --auto --rotation normal' % (screens[2].name, screens[1].name))
  cl(' '.join(xrandr))
  # if lid:
  #   # Move xmobar to the right screen
  #   cl('killall -s SIGUSR1 xmobar')

def wallpaper(image):
  print 'Refreshing background image: %s' % image
  #cl('feh --bg-scale "%s"' % BG_IMAGE)
  cl('feh --bg-fill "%s"' % image)

def systray(screens):
  print 'Refreshing system tray'
  cl('killall trayer')
  if len(screens) > 1:
    margin = 0 #screens[1].width
    cl('trayer --edge top --align right --SetDockType true --SetPartialStrut true --expand true --width 11 --tint 0x000000 --alpha 0 --transparent true --height 17 --margin %s &' % margin)
  else:
    cl('trayer --edge top --align right --SetDockType true --SetPartialStrut true --expand true --width 11 --tint 0x000000 --alpha 0 --transparent true --height 17 &')

def mouse(trackball):
## Set mouse
  if trackball:
    # Trackball: right handed
    cl('xmodmap -e "pointer = 1 8 3 4 5 6 7 2"')
  else:
    # Trackpad
    cl('xmodmap -e "pointer = 3 2 1 4 5 6 7 8"')
    cl('xinput set-int-prop "TPPS/2 IBM TrackPoint" "Evdev Wheel Emulation" 8 1')
    cl('xinput set-int-prop "TPPS/2 IBM TrackPoint" "Evdev Wheel Emulation Button" 8 2')

def screensaver():
    cl('killall xscreensaver')
    cl('xscreensaver -nosplash &')

def reset():
  cl('xrandr --auto')

def force(screens):
  if len(screens) > 1:
    cl('xrandr --output %s --off; xrandr --output %s --auto' % (screens[1].name, screens[1].name))

# Trackball: left handed
#xmodmap -e 'pointer = 3 8 1 4 5 6 7 2'

########
# MAIN #
########

def main():
  parser = OptionParser()
  # parser.add_option("-d", "--delay", dest="delay", metavar="SECONDS",
  #                   help="sleep for this many seconds before doing anything")
  # parser.add_option("-t", "--no-trayer",
  #                   action="store_false", dest="trayer", default=True,
  #                   help="do not initialize trayer")
  # parser.add_option("-w", "--no-wallpaper",
  #                   action="store_false", dest="wallpaper", default=True,
  #                   help="do not initialize wallpaper")
  parser.add_option("-r", "--no-reset",
                    action="store_false", dest="reset", default=True,
                    help="do not reset xrandr before starting")
  parser.add_option("-f", "--force",
                    action="store_true", dest="force", default=False,
                    help="do not reset xrandr before starting")
  parser.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="print out commands that are being executed")
  parser.add_option("-p", "--pretend",
                    action="store_true", dest="pretend", default=False,
                    help="print out commands that are being executed but do not actually run them")

  (options, args) = parser.parse_args()


  config = ConfigParser.RawConfigParser()
  config.read(os.path.join(os.environ['HOME'], 'etc/autodetect.ini'))

  if config.has_option('main', 'delay'):
   time.sleep(config.getint('main', 'delay'))

  #################
  # CONFIGURATION #
  #################

  global VERBOSE
  global PRETEND
  global RESET
  global FORCE

  VERBOSE = options.verbose
  PRETEND = options.pretend
  RESET   = options.reset
  FORCE   = options.force

  # Reset screens before doing anything
  if RESET:
    reset()

  # Get current configuration
  screens = get_screens()

  if FORCE:
    force(screens)

  # Get lid state (open/closed)
  lid = lid_state()

  # Set screen resolution
  xrandr(screens, lid)

  # Refresh screen resolution after it was modified
  screens = get_screens()

  # Set wallpaper
  if config.getboolean('main', 'wallpaper'):
    wallpaper(BG_IMAGE)

  # Start system tray
  if config.getboolean('main', 'systray'):
    systray(screens)

  # Identify mouse
  trackball = is_trackball()

  # Configure mouse
  mouse(trackball)

  #screensaver()

  ## Setup keyboard
  cl('xmodmap $HOME/.xmodmap')

if __name__ == '__main__':
  main()
