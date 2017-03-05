"""
MikeyBorgRC
Remotely controls a PicoBorg with a PS3 controller
Based on the DiddyBorg example (https://www.piborg.org/diddyborg/install)
"""
#!/usr/bin/env python3
# coding: Latin-1

# Import the libraries
import os
import time
import sys
import pygame
from   Classes import PicoBorgRev3
# Re-direct output to standard error to hide some messages from pygame
sys.stdout = sys.stderr
# Set up the PicoBorg Reverse
PBR = PicoBorgRev3.PicoBorgRev()
PBR.Init()
# If no PicoBorg Reverse was found, output a message
if not PBR.foundChip:
	BOARDS = PicoBorgRev3.ScanForPicoBorgReverse()
	if len(BOARDS) == 0:
		print("No PicoBorg Reverse found, check connection")
	else:
		print("No PicoBorg Reverse found at address %02X, but found:" % (PBR.i2cAddress))
		for board in BOARDS:
			print("    %02X (%d)" % (board, board))
	sys.exit()
PBR.ResetEpo()
# Settings for the controller. PyLint seems to think constants should be SHOUTED
AXISLEFT          = 1     # Joystick axis to read up and down
AXISLEFTINVERTED  = False # Set to true if up and down are inverted
AXISRIGHT         = 2     # Joystick axis for left/right position
AXISRIGHTINVERTED = False # Set to true if left and right are swapped
BUTTONRESETEPO    = 3     # Button number to perform an EP0 reset
BUTTONSLOW        = 8     # Button number to drive slowly when held
SLOWFACTOR        = 0.5   # Speed to slow down to when going slowly
BUTTONFASTTURN    = 9     # Joystick button for turning fast
INTERVAL          = 0.00  # Time between updates
# Set up pygame
os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()
pygame.joystick.init()
pygame.display.set_mode((1,1))
JOYSTICK = pygame.joystick.Joystick(0)
JOYSTICK.init()
# The MAIN TRY
try:
	print("Press CTRL+C to quit")
	DRIVELEFT  = 0.0
	DRIVERIGHT = 0.0
	RUNNING    = True
	HADEVENT   = False
	UPDOWN     = 0.0
	LEFTRIGHT  = 0.0
	# Loop until the keyboard is interrupted
	while RUNNING:
		# Get the latest event from the system
		HADEVENT = False
		EVENTS   = pygame.event.get()
		# Handle each event individually
		for event in EVENTS:
			if event.type == pygame.QUIT:
				RUNNING = False
			elif event.type == pygame.JOYBUTTONDOWN:
				HADEVENT = True
			elif event.type == pygame.JOYAXISMOTION:
				HADEVENT = True
			if HADEVENT:
				# Read axis positions
				if AXISLEFTINVERTED:
					DRIVELEFT = JOYSTICK.get_axis(AXISLEFT)
				else:
					DRIVELEFT = -JOYSTICK.get_axis(AXISLEFT)
				if AXISRIGHTINVERTED:
					DRIVERIGHT = -JOYSTICK.get_axis(AXISRIGHT)
				else:
					DRIVERIGHT = JOYSTICK.get_axis(AXISRIGHT)
				# Check for button presses
				if JOYSTICK.get_button(BUTTONRESETEPO):
					PBR.ResetEpo()
				if JOYSTICK.get_button(BUTTONSLOW):
					DRIVELEFT  *= SLOWFACTOR
					DRIVERIGHT *= SLOWFACTOR
				# Set the motors to the new speeds
				PBR.SetMotor1(-DRIVERIGHT)
				PBR.SetMotor2(-DRIVELEFT)
			# Change the LED to reflect the status of the EP0 latch
			PBR.SetLed(PBR.GetEpo())
		# Wait for the interval period
		time.sleep(INTERVAL)
	# Disable all drives
	PBR.MotorsOff()
except KeyboardInterrupt:
	PBR.MotorsOff()
print("Closed")
