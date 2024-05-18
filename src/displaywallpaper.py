#!/usr/bin/python

import os
import json
import subprocess
from random import randrange, seed
from os.path import join, expanduser

LIVE_DATA_FILE = expanduser("~/.wallpaperlaunch")

WALLPAPER_DIR = expanduser("~/Media/Wallpapers/")
SETS_DIR = expanduser("~/Media/Wallpapers/Sets")

VIDEO_FILETYPES = ["mp4"]
LIVE_FILETYPES = ["live"]

LEFT_DIR = join(WALLPAPER_DIR, "ActiveL")
RIGHT_DIR = join(WALLPAPER_DIR, "ActiveR")
MAIN_DIR = join(WALLPAPER_DIR, "Active")

def getHyprctlOutput(command: str) -> str:
	return json.loads(subprocess.check_output(f"hyprctl {command} -j", shell = True))

def getMonitorName(left: bool) -> str:
	target_pos = 0 if left else 1920

	monitors: list[dict] = getHyprctlOutput("monitors")
	for monitor in monitors:
		if monitor["x"] == target_pos:
			return monitor["name"]

	return monitors[0]["name"]

def setImageWallpaper(left: bool, path: str) -> subprocess.Popen:
	monitor = getMonitorName(left)
	return subprocess.Popen(["swaybg", "-o", monitor, "-i", path])

def setVideoWallpaper(left: bool, path: str):
	monitor = getMonitorName(left)
	return subprocess.Popen(["mpvpaper", "-o", "--speed=1", monitor, path])

def getVideoDuration(path: str):
	return subprocess.check_output(f"ffmpeg -i {path} 2>&1 | grep \"Duration\"| cut -d ' ' -f 4 | sed s/,//", shell = True).decode().strip()

def setLiveWallpaper(left: bool, path: str):
	monitor = getMonitorName(left)

	f = open(path, "r")
	data = json.loads(f.read())
	f.close()

	video = join(os.path.dirname(path), data["video"])

	socket = "/tmp/wp-" + monitor
	options = f"input-ipc-server={socket} --no-osd-bar --speed=1"

	loop_position = data.get("loop-position")
	if loop_position is not None:
		options += " --ab-loop-a=" + data["loop-position"]

		duration = getVideoDuration(video).removeprefix("00:")
		options += " --ab-loop-b=" + duration

	writeLiveData(monitor, socket, path)

	args = ["mpvpaper", "-o", options, monitor, video]
	return subprocess.Popen(args)

def writeLiveData(monitor: str, socket: str, live_path: str):
	data = {}

	if os.path.isfile(LIVE_DATA_FILE):
		f = open(LIVE_DATA_FILE, "r")
		data = json.loads(f.read())
		f.close()

	data[monitor] = {"socket": socket, "live": live_path}

	f = open(LIVE_DATA_FILE, "w")
	f.write(json.dumps(data))
	f.close()

def setWallpapers(left_path: str, right_path: str):
	if os.path.isfile(LIVE_DATA_FILE):
		os.remove(LIVE_DATA_FILE)
	os.system("killall swaybg")
	os.system("killall mpvpaper")

	global left_proc
	global right_proc
	left_proc = None
	right_proc = None

	def tryFileTypes(types: list[str], onFound):
		global left_proc
		global right_proc

		for type in types:
			if left_path is not None and left_proc is None and left_path.endswith("." + type):
				left_proc = onFound(True, left_path)
			if right_path is not None and right_proc is None and right_path.endswith("." + type):
				right_proc = onFound(False, right_path)

	tryFileTypes(VIDEO_FILETYPES, setVideoWallpaper)
	tryFileTypes(LIVE_FILETYPES, setLiveWallpaper)

	if left_path is not None and left_proc is None:
		left_proc = setImageWallpaper(True, left_path)
	if right_path is not None and right_proc is None:
		right_proc = setImageWallpaper(False, right_path)

	try:
		if left_proc is not None:
			left_proc.wait()
		if right_proc is not None:
			right_proc.wait()
	except:
		if os.path.isfile(LIVE_DATA_FILE):
			os.remove(LIVE_DATA_FILE)

		if left_proc is not None:
			left_proc.kill()
		if right_proc is not None:
			right_proc.kill()

def getRandomWallpaper(directory: str, used_files: list):
	files = []

	for file in os.listdir(directory):
		if file.startswith("."):
			continue

		file_path = join(directory, file)
		if file.endswith(".set"):
			f = open(file_path, "r")
			set_content = f.read().strip()
			f.close()

			set_path = join(SETS_DIR, set_content)

			if not os.path.isdir(set_path):
				print("Set not found: " + set_path)
				continue

			for set_file in os.listdir(set_path):
				if set_file.startswith("."):
					continue

				set_file_path = join(set_path, set_file)
				if set_file_path in used_files:
					continue
				files.append(set_file_path)

			continue

		if file_path in used_files:
			continue

		files.append(file_path)

	if len(files) > 0:
		ret = files[randrange(len(files))]
		used_files.append(ret)
		return ret

	return None

def main():
	seed()

	wallpapers = {"left": "", "right": ""}
	used_files = []

	def getSide(side, used):
		if os.path.isdir(side[1]):
			file = getRandomWallpaper(side[1], used)
			if file is not None:
				wallpapers[side[0]] = file
				return

		wallpapers[side[0]] = getRandomWallpaper(MAIN_DIR, used)

	for side in (("left", LEFT_DIR), ("right", RIGHT_DIR)):
		getSide(side, used_files)

	if wallpapers["right"] is None:
		getSide(("right", RIGHT_DIR), [])

	print(wallpapers)

	setWallpapers(wallpapers["left"], wallpapers["right"])

if __name__ == "__main__":
	main()
