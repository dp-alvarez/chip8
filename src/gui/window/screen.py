import numpy as np
import pygame as pyg
from .. import gui


def render():
	pyg_screen_array[:] = window_bg_mapped
	newscreen = np.array(gui.screen.data, dtype='bool', copy=False).reshape(gui.screen.shape)
	newscreen = newscreen.repeat(gui.config.draw_size, axis=0).repeat(gui.config.draw_size, axis=1)
	mask[0:newscreen.shape[0], 0:newscreen.shape[1]] = newscreen
	pyg_screen_array[mask] = draw_color_mapped
	pyg.surfarray.blit_array(pyg_screen, pyg_screen_array)


def init():
	global pyg_screen, pyg_screen_array, mask, draw_color_mapped, window_bg_mapped
	pyg_screen = pyg.surface.Surface(gui.config.screen_size)
	pyg_screen_array = pyg.surfarray.array2d(pyg_screen)
	mask = np.zeros(pyg_screen_array.shape, dtype='bool')
	draw_color_mapped = pyg_screen.map_rgb(gui.config.draw_color)
	window_bg_mapped = pyg_screen.map_rgb(gui.config.window_bg)

	render()
