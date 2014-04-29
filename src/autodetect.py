#!/usr/bin/env python

import os
import re
import time
from optparse import OptionParser
from collections import namedtuple
import ConfigParser


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

def home(path):
  return

config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.environ['HOME'], 'etc/autodetect.ini'))

if config.has_option('main', 'delay'):
 time.sleep(config.getint('main', 'delay'))

#################
# CONFIGURATION #
#################

VERBOSE = options.verbose
PRETEND = options.pretend
RESET   = options.reset
FORCE   = options.force

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

LID_STATE = '/proc/acpi/button/lid/LID/state'

#########
# UTILS #
#########

CONNECTED_PATTERN = re.compile(r'([A-Z0-9]+) (connected|connected primary) ([0-9]+)')

Screen = namedtuple('Screen', 'name width')

def get_screens():
  '''Get all screen names'''
  screens = []
  for line in os.popen('xrandr'):
    matcher = CONNECTED_PATTERN.match(line)
    if matcher:
      screens.append(Screen(name=matcher.group(1), width=int(matcher.group(3))))
  print 'Active screens: %s' % ', '.join([s.name for s in screens])
  return screens

def cl(command):
  if VERBOSE:
    print '$', command
  if not PRETEND:
    os.popen(command)

def is_trackball():
  '''Are we using a trackball?'''
  for line in os.popen('lsusb'):
    if TRACKBALL in line:
      print 'Found trackball'
      return True
  print 'Found trackpad'
  return False

def lid_state():
  lid = None
  with open(LID_STATE, 'r') as f:
    lid = 'open' in f.read()
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
  xrandr = ['xrandr --output "%s" --%s' % (screens[0].name, state)]
  if len(screens) > 1:
    xrandr.append('--output "%s" --left-of "%s" --auto' % (screens[1].name, screens[0].name))
  cl(' '.join(xrandr))
  # if lid:
  #   # Move xmobar to the right screen
  #   cl('killall -s SIGUSR1 xmobar')

def wallpaper():
  print 'Refreshing background image: %s' % BG_IMAGE
  #cl('feh --bg-scale "%s"' % BG_IMAGE)
  cl('feh --bg-fill "%s"' % BG_IMAGE)

def systray(screens):
  print 'Refreshing system tray'
  cl('killall trayer')
  if len(screens) > 1:
    margin = screens[0].width + 1
    cl('trayer --edge top --align right --SetDockType true --SetPartialStrut true --expand true --width 6 --tint 0x000000 --alpha 0 --transparent true --height 17 --margin %s &' % margin)
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
  wallpaper()

# Start system tray
if config.getboolean('main', 'systray'):
  systray(screens)

# Identify mouse
trackball = is_trackball()

# Configure mouse
mouse(trackball)

screensaver()

## Setup keyboard
cl('xmodmap $HOME/.xmodmap')
