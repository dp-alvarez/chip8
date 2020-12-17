import pygame as pyg
from . import window, grid, overlay, input


def gui_init(_config, _screen, _keyboard):
	global config, screen, keyboard
	config = _config
	screen = _screen
	keyboard = _keyboard

	grid.init()
	overlay.init()
	window.init()
	input.init()


def gui_quit():
	pyg.quit()
