import pygame as pyg
from .. import gui


def render(ups, fps):
	ups = f'UPS: {ups:,.0f}'
	fps = f'FPS: {fps:,}'
	ups = pyg_font.render(ups, False, gui.config.window.draw_color)
	fps = pyg_font.render(fps, False, gui.config.window.draw_color)
	overlay.fill(gui.config.window.window_bg)
	overlay.blit(ups, (0,0))
	overlay.blit(fps, (0,gui.config.window.font_size))


def init():
	global overlay, pyg_font
	overlay = pyg.surface.Surface(gui.config.window.overlay_size)
	pyg.font.init()
	pyg_font = pyg.font.SysFont(gui.config.window.font, gui.config.window.font_size)

	render(0.0, 0.0)
