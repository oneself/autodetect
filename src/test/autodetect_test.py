from nose.tools import *
from mock import patch
import autodetect

XRANDR_2 = '''Screen 0: minimum 320 x 200, current 3760 x 1920, maximum 32767 x 32767
LVDS1 connected (normal left inverted right x axis y axis)
   1366x768       60.0 +
   1360x768       59.8     60.0
   1024x768       60.0
   800x600        60.3     56.2
   640x480        59.9
VGA1 disconnected 1200x1920+2560+0 left (normal left inverted right x axis y axis) 0mm x 0mm
HDMI1 disconnected (normal left inverted right x axis y axis)
DP1 disconnected (normal left inverted right x axis y axis)
HDMI2 disconnected (normal left inverted right x axis y axis)
HDMI3 disconnected (normal left inverted right x axis y axis)
DP2 connected primary 2560x1600+0+0 (normal left inverted right x axis y axis) 641mm x 401mm
   2560x1600      60.0*+
   1920x1440      60.0
   1920x1200      59.9
   1920x1080      60.0     50.0     59.9     24.0     24.0
   1920x1080i     60.1     50.0     60.0
   1600x1200      60.0
   1280x1024      75.0     60.0
   1280x800       59.8
   1152x864       75.0
   1280x720       60.0     50.0     59.9
   1024x768       75.1     60.0
   800x600        75.0     60.3
   720x576        50.0
   720x480        60.0     59.9
   640x480        75.0     60.0     59.9
   720x400        70.1
DP3 disconnected (normal left inverted right x axis y axis)
VIRTUAL1 disconnected (normal left inverted right x axis y axis)
  1920x1200 (0xf8)  154.0MHz
        h: width  1920 start 1968 end 2000 total 2080 skew    0 clock   74.0KHz
        v: height 1200 start 1203 end 1209 total 1235           clock   60.0Hz
'''.split('\n')

XRANDR_3 = '''Screen 0: minimum 320 x 200, current 2560 x 1600, maximum 32767 x 32767
LVDS1 connected (normal left inverted right x axis y axis)
   1366x768       60.0 +
   1360x768       59.8     60.0
   1024x768       60.0
   800x600        60.3     56.2
   640x480        59.9
VGA1 connected (normal left inverted right x axis y axis)
   1920x1200      60.0 +
   1600x1200      60.0
   1280x1024      75.0     60.0
   1152x864       75.0
   1024x768       75.1     60.0
   800x600        75.0     60.3
   640x480        75.0     60.0
   720x400        70.1
HDMI1 disconnected (normal left inverted right x axis y axis)
DP1 disconnected (normal left inverted right x axis y axis)
HDMI2 disconnected (normal left inverted right x axis y axis)
HDMI3 disconnected (normal left inverted right x axis y axis)
DP2 connected primary 2560x1600+0+0 (normal left inverted right x axis y axis) 641mm x 401mm
   2560x1600      60.0*+
   1920x1440      60.0
   1920x1200      59.9
   1920x1080      60.0     50.0     59.9     24.0     24.0
   1920x1080i     60.1     50.0     60.0
   1600x1200      60.0
   1280x1024      75.0     60.0
   1280x800       59.8
   1152x864       75.0
   1280x720       60.0     50.0     59.9
   1024x768       75.1     60.0
   800x600        75.0     60.3
   720x576        50.0
   720x480        60.0     59.9
   640x480        75.0     60.0     59.9
   720x400        70.1
DP3 disconnected (normal left inverted right x axis y axis)
VIRTUAL1 disconnected (normal left inverted right x axis y axis)
'''.split('\n')

TRACKBALL_TRUE = '''Bus 002 Device 002: ID 8087:0024 Intel Corp. Integrated Rate Matching Hub
Bus 002 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 005: ID 04f2:b2ea Chicony Electronics Co., Ltd Integrated Camera [ThinkPad]
Bus 001 Device 004: ID 0a5c:21e6 Broadcom Corp. BCM20702 Bluetooth 4.0 [ThinkPad]
Bus 001 Device 003: ID 147e:2020 Upek TouchChip Fingerprint Coprocessor (WBF advanced mode)
Bus 001 Device 002: ID 8087:0024 Intel Corp. Integrated Rate Matching Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 006: ID 05f3:0007 PI Engineering, Inc. Kinesis Advantage PRO MPC/USB Keyboard
Bus 003 Device 005: ID 05f3:0081 PI Engineering, Inc. Kinesis Integrated Hub
Bus 003 Device 004: ID 047d:1020 Kensington Expert Mouse Trackball
Bus 003 Device 007: ID 1852:7022 GYROCOM C&C Co., LTD
Bus 003 Device 002: ID 0424:2514 Standard Microsystems Corp. USB 2.0 Hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
'''.split('\n')

TRACKBALL_FALSE = '''Bus 002 Device 002: ID 8087:0024 Intel Corp. Integrated Rate Matching Hub
Bus 002 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 005: ID 04f2:b2ea Chicony Electronics Co., Ltd Integrated Camera [ThinkPad]
Bus 001 Device 004: ID 0a5c:21e6 Broadcom Corp. BCM20702 Bluetooth 4.0 [ThinkPad]
Bus 001 Device 003: ID 147e:2020 Upek TouchChip Fingerprint Coprocessor (WBF advanced mode)
Bus 001 Device 002: ID 8087:0024 Intel Corp. Integrated Rate Matching Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 006: ID 05f3:0007 PI Engineering, Inc. Kinesis Advantage PRO MPC/USB Keyboard
Bus 003 Device 005: ID 05f3:0081 PI Engineering, Inc. Kinesis Integrated Hub
Bus 003 Device 007: ID 1852:7022 GYROCOM C&C Co., LTD
Bus 003 Device 002: ID 0424:2514 Standard Microsystems Corp. USB 2.0 Hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
'''.split('\n')

LID_OPEN = '''state:      open
'''

LID_CLOSED = '''state:      closed
'''

@patch('autodetect.cl')
def test_get_screens_2(cl_mock):
  cl_mock.return_value = XRANDR_2
  screens = autodetect.get_screens()
  eq_([autodetect.Screen(name='LVDS1', width=1366),
       autodetect.Screen(name='DP2', width=2560)],
      screens)

@patch('autodetect.cl')
def test_get_screens_3(cl_mock):
  cl_mock.return_value = XRANDR_3
  screens = autodetect.get_screens()
  eq_([autodetect.Screen(name='LVDS1', width=1366),
       autodetect.Screen(name='VGA1', width=1920),
       autodetect.Screen(name='DP2', width=2560)],
      screens)

@patch('autodetect.cl')
def test_is_trackball_true(cl_mock):
  cl_mock.return_value = TRACKBALL_TRUE
  eq_(True, autodetect.is_trackball())

@patch('autodetect.cl')
def test_is_trackball_false(cl_mock):
  cl_mock.return_value = TRACKBALL_FALSE
  eq_(False, autodetect.is_trackball())

@patch('autodetect.cl')
def test_lid_state_open(cl_mock):
  cl_mock.return_value = LID_OPEN
  eq_(True, autodetect.lid_state())

@patch('autodetect.cl')
def test_lid_state_open(cl_mock):
  cl_mock.return_value = LID_CLOSED
  eq_(False, autodetect.lid_state())

@patch('autodetect.cl')
def test_xrandr_1(cl_mock):
  autodetect.xrandr([autodetect.Screen(name='LVDS1', width=1366)], True)
  eq_("call('xrandr --output LVDS1 --auto')", str(cl_mock.call_args))

@patch('autodetect.cl')
def test_xrandr_2(cl_mock):
  autodetect.xrandr([autodetect.Screen(name='LVDS1', width=1366),
                     autodetect.Screen(name='DP2', width=2560)], False)
  eq_("call('xrandr --output LVDS1 --off --output DP2 --left-of LVDS1 --auto')",
      str(cl_mock.call_args))

@patch('autodetect.cl')
def test_xrandr_3(cl_mock):
  autodetect.xrandr([autodetect.Screen(name='LVDS1', width=1366),
                     autodetect.Screen(name='VGA1', width=1920),
                     autodetect.Screen(name='DP2', width=2560)], False)
  eq_("call('xrandr --output LVDS1 --off --output VGA1 --rotation left --auto --output DP2 --left-of VGA1 --auto --rotation normal')",
      str(cl_mock.call_args))

@patch('autodetect.cl')
def test_systray_1(cl_mock):
  autodetect.systray([autodetect.Screen(name='LVDS1', width=1366)])
  eq_("call('trayer --edge top --align right --SetDockType true --SetPartialStrut true --expand true --width 11 --tint 0x000000 --alpha 0 --transparent true --height 17 &')",
      str(cl_mock.call_args))

@patch('autodetect.cl')
def test_systray_2(cl_mock):
  autodetect.systray([autodetect.Screen(name='LVDS1', width=1366),
                      autodetect.Screen(name='DP2', width=2560)])
  eq_("call('trayer --edge top --align right --SetDockType true --SetPartialStrut true --expand true --width 11 --tint 0x000000 --alpha 0 --transparent true --height 17 --margin 0 &')",
      str(cl_mock.call_args))

@patch('autodetect.cl')
def test_systray_3(cl_mock):
  autodetect.systray([autodetect.Screen(name='LVDS1', width=1366),
                      autodetect.Screen(name='VGA1', width=1920),
                      autodetect.Screen(name='DP2', width=2560)])
  eq_("call('trayer --edge top --align right --SetDockType true --SetPartialStrut true --expand true --width 11 --tint 0x000000 --alpha 0 --transparent true --height 17 --margin 0 &')",
      str(cl_mock.call_args))
