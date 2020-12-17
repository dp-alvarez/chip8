import numpy as np
import pygame as pyg
from . import gui, overlay, grid, input


def draw_window():
	pyg_screen_array[:] = window_bg_mapped
	newscreen = np.array(gui.screen.data, dtype='bool', copy=False).reshape(gui.screen.shape)
	newscreen = newscreen.repeat(gui.config.draw_size, axis=0).repeat(gui.config.draw_size, axis=1)
	mask[0:newscreen.shape[0], 0:newscreen.shape[1]] = newscreen
	pyg_screen_array[mask] = draw_color_mapped
	pyg.surfarray.blit_array(pyg_screen, pyg_screen_array)

	pyg_window.blit(overlay.overlay, gui.config.overlay_pos)
	pyg_window.blit(pyg_screen, gui.config.screen_pos)
	pyg_window.blit(grid.grid, gui.config.screen_pos)
	pyg.display.update()


def update_window(now):
	#pylint: disable=used-before-assignment
	global last_window_update

	if now-last_window_update < gui.config.draw_interval:
		return
	last_window_update = now
	overlay.n_frames += 1

	draw_window()
	input.update_input()


def init():
	global last_window_update
	last_window_update = 0

	global pyg_window, pyg_screen
	pyg.display.init()
	pyg_window = pyg.display.set_mode(gui.config.window_size)
	pyg.display.set_caption(gui.config.caption)
	pyg_screen = pyg.surface.Surface(gui.config.screen_size)

	global pyg_screen_array, mask, draw_color_mapped, window_bg_mapped
	pyg_screen_array = pyg.surfarray.array2d(pyg_screen)
	mask = np.zeros(pyg_screen_array.shape, dtype='bool')
	draw_color_mapped = pyg_screen.map_rgb(gui.config.draw_color)
	window_bg_mapped = pyg_screen.map_rgb(gui.config.window_bg)

	pyg_window.fill(gui.config.window_bg)
