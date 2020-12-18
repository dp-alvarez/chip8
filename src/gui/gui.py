import pygame as pyg
from . import window
from . import perf


def init(_config, _screen, _keyboard):
	global config, screen, keyboard
	config = _config
	screen = _screen
	keyboard = _keyboard

	perf.init()
	window.init()


def gui_quit():
	pyg.quit()
