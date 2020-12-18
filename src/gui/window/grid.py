import pygame as pyg
from .. import gui


def create_grid():
	grid = pyg.surface.Surface(gui.config.window.screen_size)
	grid.set_colorkey(gui.config.window.window_bg, pyg.RLEACCEL)
	grid.fill(gui.config.window.window_bg)

	xend = gui.config.window.draw_size * gui.config.system.screen_size[0]
	yend = gui.config.window.draw_size * gui.config.system.screen_size[1]
	for i in range(gui.config.system.screen_size[0]+1):
		x = i*gui.config.window.draw_size
		pyg.draw.line(grid, gui.config.window.grid_color, (x,0), (x,yend), 1)
	for i in range(gui.config.system.screen_size[1]+1):
		y = i*gui.config.window.draw_size
		pyg.draw.line(grid, gui.config.window.grid_color, (0,y), (xend,y), 1)

	return grid


def init():
	global grid
	grid = create_grid()
