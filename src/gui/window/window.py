import pygame as pyg
from .. import gui, perf
from . import overlay, grid, input, screen


def draw():
	pyg_window.blit(overlay.overlay, gui.config.window.overlay_pos)
	pyg_window.blit(screen.pyg_screen, gui.config.window.screen_pos)
	pyg_window.blit(grid.grid, gui.config.window.screen_pos)
	pyg.display.update()


def update(now):
	#pylint: disable=used-before-assignment
	global last_update

	if now-last_update < gui.config.window.draw_interval:
		return
	last_update = now
	perf.n_frames += 1

	screen.render()
	draw()
	input.update()


def init_window():
	global last_update
	last_update = 0

	global pyg_window
	pyg.display.init()
	pyg_window = pyg.display.set_mode(gui.config.window.window_size)
	pyg.display.set_caption(gui.config.window.caption)
	pyg_window.fill(gui.config.window.window_bg)

	draw()


def init():
	grid.init()
	overlay.init()
	screen.init()
	init_window()
	input.init()
