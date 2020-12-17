import pygame as pyg
from . import gui


def create_grid():
	grid = pyg.surface.Surface(gui.config.screen_size)
	grid.set_colorkey(gui.config.window_bg, pyg.RLEACCEL)
	grid.fill(gui.config.window_bg)

	xend = gui.config.draw_size * gui.config.system.screen_size[0]
	yend = gui.config.draw_size * gui.config.system.screen_size[1]
	for i in range(gui.config.system.screen_size[0]+1):
		x = i*gui.config.draw_size
		pyg.draw.line(grid, gui.config.grid_color, (x,0), (x,yend), 1)
	for i in range(gui.config.system.screen_size[1]+1):
		y = i*gui.config.draw_size
		pyg.draw.line(grid, gui.config.grid_color, (0,y), (xend,y), 1)

	return grid


def init():
	global grid
	grid = create_grid()
