import time
import datetime
import winsound
import os
import sys
import platform
import urllib.request
import json
import webbrowser
import threading
import queue

program_name = "hsnotify"

credit_line = "Program by Voxalice (https://github.com/voxalice2/" + program_name + "/)"

version = {}
version["number"] = "1.0"
version["date"] = "2025-10-06"
version["info"] = "Initial release"

# Setting initializations

settings = {}
settings["help"] = {}
settings["accept"] = {}

settings["delay"] = 10.25
settings["sound"] = "beep"
settings["uri"] = "https://www.homestuck.com/assets/json/adventure_log.json"
settings["link"] = "https://www.homestuck.com/story/"

settings["help"]["delay"] = 'The number of seconds between update checks. (Try not to set this too low.)'
settings["help"]["sound"] = 'The path to a WAV file that plays when an update is found (only on Windows), OR "beep" to use the system beep, OR nothing to turn off sound.'
settings["help"]["uri"] = "The URI of the adventure log to check for updates. (If this isn't a valid adventure log JSON file, crashing may occur.)"
settings["help"]["link"] = "The URI of the webcomic to go to when an update is found."

settings["accept"]["delay"] = "positive numbers"
settings["accept"]["sound"] = "strings"
settings["accept"]["uri"] = "strings"
settings["accept"]["link"] = "strings"

# HIDDEN setting initializations

settings["fake_update"] = False

# Functions

def clear():
	print("\033c\033[3J", end='') # ANSI escape codes

def newline():
	print("")

def log(text, newline = True):
	print(datetime.datetime.now(), " / ", str(text), end = "\n" if newline else "")

def log_setting(setting):
	log('"' + setting + '" = ' + str(settings[setting]))

def check():
	global beeper
	global stop_beeping
	global latest_page

	clear()
	log("(" + program_name + " launched - press Ctrl+C to pause and view settings, OR press Enter to start checking for updates)\n")

	empty_input("")

	while True:
		log("Checking for a new update every ", False)
		print(settings["delay"], "seconds... press Ctrl+C to view settings")

		updated = False

		if settings["fake_update"]:
			updated = True
			old_latest_page = 0
		else:
			checking_page = find_latest_page()

			if checking_page != latest_page:
				updated = True
				old_latest_page = latest_page
				latest_page = checking_page

		if updated:
			try:
				upd8(old_latest_page)
			except KeyboardInterrupt:
				stop_beeping = True
				check()

		time.sleep(settings["delay"])

def find_latest_page():
	# Request log

	req = urllib.request.Request(settings['uri'])
	req.add_header('Range', 'bytes=0-612')
	res = urllib.request.urlopen(req)

	# Get first item specifically (this saves bandwidth and memory!)

	final_string = ""

	for i in range(1, 500):
		current_byte = str(res.read(1).decode('UTF-8'))
		final_string += current_byte

		if (current_byte) == "}":
			final_string += "]"
			break

	# Process resulting JSON

	res_JSON = json.loads(final_string)

	return res_JSON[0]["id"]

def upd8(old_latest_page):
	global beeper
	global stop_beeping

	settings["fake_update"] = False
	stop_beeping = False

	clear()
	log("New update found! Press Enter to go to the new update, or Ctrl+C to go back to checking")

	# Start beeping in a new thread to avoid blocking input
	beeper = threading.Thread(target = beep, args = ())
	beeper.start()

	_ = empty_input("")
	
	stop_beeping = True
	webbrowser.open_new_tab(settings["link"] + str(old_latest_page + 1))

	raise KeyboardInterrupt # Pretend that Ctrl+C has been pressed to break out of this function

def beep():
	global stop_beeping
	while True:
		if stop_beeping:
			break

		if platform.system() == "Windows":
			if (settings["sound"] == "beep"):
				winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
				time.sleep(1.025)
			else:
				winsound.PlaySound(settings["sound"], 0)
		else:
			if (settings["sound"] != ""):
				print('\a', end = "")
				time.sleep(1.025)
	
def settings_menu():
	try:
		while True:
			clear()
			log(credit_line)
			log("Version " + version["number"] + " (" + version["date"]  + ") - " + version["info"])
			newline()
			log("Settings:")
			log_setting("delay")
			log_setting("sound")
			log_setting("uri")
			log_setting("link")
			log('Press Ctrl+C to quit, OR type "test" to trigger an update notification, OR type nothing to go back to checking')

			input_setting = empty_input("Type the name of a setting to change it: ")

			newline() # ??? this fixes a bug where the settings menu would appear repeatedly after pressing Ctrl+C. don't ask

			if (input_setting == ""):
				hsnotify()
				return 0

			settings["fake_update"] = False
			if (input_setting == "test"):
				settings["fake_update"] = True
				hsnotify()
				return 0

			if input_setting in settings:
				input_invalid = True

				try:
					while input_invalid:
						log_setting(input_setting)
						log(settings["help"][input_setting])
						input_value = empty_input("Change this setting's value to: ")

						input_invalid = False

						if (settings["accept"][input_setting] == "positive numbers"):
							try:
								input_value = float(input_value)
							except ValueError:
								input_value = -413 # make input_value invalid without causing errors

							if (input_value < 0):
								input_invalid = True

						if (settings["accept"][input_setting] == "strings"):
							input_value = str(input_value)

						if input_invalid:
							log("That input was invalid; this setting only accepts " + settings["accept"][input_setting] + ".")
						else:
							settings[input_setting] = input_value

				except KeyboardInterrupt:
					sys.exit()

	except KeyboardInterrupt:
		sys.exit()

def empty_input(text):
	log("", False)

	try:
		return input(text)
	except EOFError:
		return "" # no input received, just move on!

def hsnotify():
	try:
		check()

	except KeyboardInterrupt:
		settings_menu()

# Extra initializations that rely on functions

clear()
log("Loading...")
latest_page = find_latest_page()

# Start hsnotify

hsnotify()