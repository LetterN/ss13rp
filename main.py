import pypresence
import time
import win32gui
import win32process
import psutil
import sys
import util
import requests
import time
from config import *
import webbrowser

while True:
	try:
		rp = pypresence.Client(client_id)
		rp.start()
		break
	except:
		time.sleep(15)

def jointhingy(one_arg):
	#insert browserpopopen with ip+port
	#browser = webbrowser.get('windows-default') dosent fucking work ree
	webbrowser.open_new('byond://bagil.tgstation13.org')
	print("SOMEONE CALLED IT WOOOOOOOT APC DESTROYED MISSION ACCOMPLISHED\n\n\n\n\nalso arg: "+str(one_arg))

rp.register_event("ACTIVITY_JOIN", jointhingy)	#handle joinshits

def json_obj_exist(jsom, search):
	#print(str(search in jsom))
	return search in jsom	#return true for fuck sakes

def get_hwnds_for_pid (pid):
	def callback (hwnd, hwnds):
		if win32gui.IsWindowVisible (hwnd) and win32gui.IsWindowEnabled (hwnd):
			_, found_pid = win32process.GetWindowThreadProcessId (hwnd)
			if found_pid == pid:
				hwnds.append (hwnd)
		return True
	hwnds = []
	win32gui.EnumWindows(callback, hwnds)
	return hwnds

def get_server():
	p = [proc for proc in psutil.process_iter() if proc.name() == "dreamseeker.exe"]
	p = p[0]

	windows=get_hwnds_for_pid(p.pid)
	windowtitles = [i for i in [str(win32gui.GetWindowText(item))
					for item in windows] if i != ""]
	for title in windowtitles:
		if not title == "Space Station 13":
			for i in servers.keys():
				if title.startswith(i):
					if LAZYLOGLEVEL >= 2:
						print("Server info: "+str(servers[i]))
					return servers[i]
		else:
			server = "ss13"
			return servers[server]

while True:
	try:
		server = get_server()
		activity = {"large_text": server[0]+": Debug edition", "large_image":server[1]}

		if len(server) >= 5:
			try:
				if server[4] == "fetch":
					status = util.fetch(server[2], server[3], "status")
					if LAZYLOGLEVEL == 3:
						print("Status (fetch): "+str(status))
				elif server[4] == "http":
					status = requests.get(server[2]).json()
					if LAZYLOGLEVEL == 3:
						print("Status (fetch): "+str(status))

				if server[0] in ["Bagil Station", "Terry Station", "Sybil Station", "Citadel Station", "FTL13", "TerraGov Marine Corps"]:
					activity["start"] = int(time.time())-int(status["round_duration"])
					activity["join"] = str(server[2])+":"+str(server[3]) #idea: when someone clicks join, they will get this link
					#activity["spectate"] = server[3]+":"+str(server[3]) #no need, do it ingame

					if json_obj_exist(status, "round_id"): #if there is status
						activity["details"] = "Map: "+status["map_name"]+" | Gamemode: "+status["mode"]+" | Round id: "+str(status["round_id"])
						activity["party_id"] = str(status["round_id"]) + " " + status["map_name"]
						#if json_obj_exist(status, "revision"):
						#	activity["party_id"] = str(status["round_id"])+" | "+status["map_name"]+" | "+status["revision"]+" | "+server[0] #making the probability of it looping very low
						#else:
						#	activity["party_id"] = str(status["round_id"])+" | "+status["map_name"]+" | "+server[0]
					else:
						activity["details"] = "Map: "+status["map_name"]+" | Gamemode: "+status["mode"]
						activity["party_id"] = server[0]+" | " + status["map_name"] + status["mode"] #need something random enough to put in here so they are on the same party

					if json_obj_exist(status, "popcap") : #if there is popcap
						activity["party_size"] = [int(status["players"])] + [int(status["popcap"])]
					else:
						activity["party_size"] = [int(status["players"])] + [90] #best guess maxcap

					if json_obj_exist(status, "gamestate"):
						actualstatus = int(status["gamestate"])
					else:
						actualstatus = 3

					if actualstatus == 0: #0: init, 1:lobbywait 2:start
						activity["state"] = "Initializing game"
						activity["instance"] = False
					elif actualstatus == 1:
						activity["state"] = "Waiting on Lobby"
						activity["instance"] = True
					elif actualstatus == 2:
						activity["state"] = "Starting"
						activity["instance"] = True
					elif actualstatus == 3:
						activity["state"] = "Started"
						activity["instance"] = True
					elif actualstatus == 4:
						activity["state"] = "Round ended!"
						activity["instance"] = False

				if server[0] in ["Baystation 12"]:
					activity["details"] = "Map: "+status["map"]+" | Players"+str(status["players"])
				elif server[0] in ["Goonstation #2","Goonstation RP #1", "Hippie Station", "BeeStation", "Yogstation 13"]:
					activity["details"] = "Map: "+status["map_name"]+" | Players"+str(status["players"])
				elif server[0] in ["VOREStation"]: #apparently this fucker dosen't return map data
					activity["details"] = "Gamemode: "+status["mode"]+" | Players"+status["players"]

				if server[0] in ["Goonstation #2","Goonstation RP #1"]:
					activity["start"] = int(time.time())-int(status["elapsed"])
				elif server[0] in ["Hippie Station", "BeeStation", "Yogstation 13"]:
					activity["start"] = int(time.time())-int(status["round_duration"])
				elif server[0] in ["VOREStation"]: #andd also it fucking returns time (in string) not in unicode-format!
					ittimetostop = status["roundduration"]
					ittimetostop = ittimetostop.split(':')
					if len(ittimetostop) >= 3:	#hr, min, sec
						activity["start"] = int(time.time())-(((int(ittimetostop[0])*60)*60) + (int(ittimetostop[1])*60) + int(ittimetostop[2]))
					else:					#min, sec
						activity["start"] = int(time.time())-((int(ittimetostop[0])*60) + int(ittimetostop[1]))

			except Exception as E:
				print("Metainfo ERROR: "+str(E))
				pass

		rp.set_activity(**activity)
		if LAZYLOGLEVEL >= 2:
			print("RP Activity JSON: "+str(activity))#spam them the json
		time.sleep(15)

	except Exception as e:
		print("Making metainfo ERROR: "+str(e))
		time.sleep(10)
		try:
			rp.clear_activity()
			time.sleep(5)
		except Exception as e:
			print("Failed clearing activity ERROR:"+str(e))
			while True:
				try:
					rp = pypresence.Client(client_id)
					rp.start()
					break
				except:
					time.sleep(20)