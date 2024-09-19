#!/etc/profiles/per-user/toaster/bin/python

import os
import json
import subprocess
import argparse
from os.path import expanduser

LIVE_DATA_FILE = expanduser("~/.wallpaperlaunch")

def performWorkspaceChangedAction(data: dict, action: dict, current_workspace: dict, previous_workspace: dict, going_left: bool, is_session_new: bool, workspaces: list[dict]):
	monitor = current_workspace["monitor"]
	socket = data[monitor]["socket"]

	only_on_empty = action.get("only-on-empty") == True
	if only_on_empty and current_workspace["windows"] > 0:
		return

	only_going_to_right = action.get("only-going-to-right") == True
	if only_going_to_right and going_left:
		return

	is_new = current_workspace["windows"] == 0
	if is_new:
		for workspace in workspaces:
			if workspace["monitor"] != monitor:
				continue

			if workspace["id"] > current_workspace["id"]:
				is_new = False

	only_on_new = action.get("only-on-new") == True
	if only_on_new and not is_new:
		return
	
	only_on_session_new = action.get("only-on-session-new") == True
	if only_on_session_new and (not is_session_new or not is_new):
		return

	seek_position = action.get("seek-position")
	if seek_position is not None:
		os.system(f"echo 'seek {seek_position} absolute' | socat - {socket}")

def onParseFailed(exception: Exception):
	relative_path = os.path.relpath(
		LIVE_DATA_FILE,
		expanduser("~/")
	)
	os.system(f"notify-send 'Parsing ~/{relative_path} failed' '{exception}'")

def getData():
	if not os.path.isfile(LIVE_DATA_FILE):
		return None
	
	f = open(LIVE_DATA_FILE, "r")
	
	try:
		return json.loads(f.read())
	except Exception as e:
		onParseFailed(e)
		raise e
	finally:
		f.close()

def setData(data: dict):
	f = open(LIVE_DATA_FILE, "w")
	f.write(json.dumps(data))
	f.close()

def getHyprctlOutput(command: str) -> str:
	return json.loads(subprocess.check_output(f"hyprctl {command} -j", shell = True))

def getMonitorName(left: bool) -> str:
	target_pos = 0 if left else 1920
	
	monitors: list[dict] = getHyprctlOutput("monitors")
	for monitor in monitors:
		if monitor["x"] == target_pos:
			return monitor["name"]

	return monitors[0]["name"]

def switchWorkspace(left: bool, move_window: bool = False):
	workspaces = getHyprctlOutput("workspaces")
	original_workspace = getHyprctlOutput("activeworkspace")
	monitor = original_workspace["monitor"]

	# Don't allow a workspace to be created if already in an empty one
	if not left and original_workspace["windows"] == 0:
		
		allow_switch = False
		for workspace in workspaces:
			if workspace["monitor"] != monitor:
				continue

			# Allow switch if there is an existing workspace to the right
			if workspace["id"] > original_workspace["id"]:
				allow_switch = True
		
		if not allow_switch:
			return

	command = "movetoworkspace" if move_window else "workspace"
	target_workspace = "r-1" if left else "r+1"

	os.system(f"hyprctl dispatch {command} {target_workspace}")
	
	data = getData()
	if data is None or not monitor in data:
		return

	f = open(data[monitor]["live"], "r")
	
	try:
		live_data = json.loads(f.read())
	except Exception as e:
		onParseFailed(e)
		raise e
	finally:
		f.close()

	action_config = live_data.get("on-workspace-changed")
	if action_config is None:
		return

	opened_workspaces = data[monitor].get("opened_workspaces")
	if opened_workspaces is None:
		opened_workspaces = [original_workspace["id"]]
		data[monitor]["opened_workspaces"] = opened_workspaces
	
	new_workspace = getHyprctlOutput("activeworkspace")
	
	is_new = False
	if not new_workspace["id"] in opened_workspaces:
		is_new = True
		opened_workspaces.append(new_workspace["id"])

	setData(data)

	performWorkspaceChangedAction(data, action_config, new_workspace, original_workspace, left, is_new, workspaces)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("direction", choices=["left", "right"])
	parser.add_argument("-m", "--move", action="store_true")

	args = parser.parse_args()
	
	move_window = args.move
	left = args.direction == "left"

	switchWorkspace(left, move_window)

if __name__ == "__main__":
	main()
