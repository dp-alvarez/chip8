import pygame as pyg
from . import gui
from .exceptions import *


def update_input():
	pressed = pyg.key.get_pressed()
	for key,button in gui.config.keymap.items():
		gui.keyboard[button] = bool(pressed[key])

	for e in pyg.fastevent.get():
		if e.type == pyg.QUIT:
			raise WindowClose


def init():
	pyg.fastevent.init()
