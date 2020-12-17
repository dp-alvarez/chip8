import pygame as pyg
from . import gui


def get_average():
	if ups_hist:
		return sum(ups_hist)/(len(ups_hist)*gui.config.perf_interval)
	return 0


def render_overlay(ups, fps):
	ups = f'UPS: {ups:,.0f}'
	fps = f'FPS: {fps:,}'
	ups = pyg_font.render(ups, False, gui.config.draw_color)
	fps = pyg_font.render(fps, False, gui.config.draw_color)
	overlay.fill(gui.config.window_bg)
	overlay.blit(ups, (0,0))
	overlay.blit(fps, (0,gui.config.font_size))


def update_overlay(now):
	#pylint: disable=used-before-assignment
	global last_perf_update, n_updates, n_frames, skip_perf

	if now-last_perf_update < gui.config.perf_interval:
		return
	last_perf_update = now

	if skip_perf:
		n_frames = 0
		n_updates = 0
		skip_perf = False
		return

	ups = n_updates/gui.config.perf_interval
	fps = n_frames/gui.config.perf_interval
	render_overlay(ups, fps)

	ups_hist.append(n_updates)
	n_updates = 0
	n_frames = 0


def init():
	global overlay, ups_hist, n_frames, n_updates, last_perf_update, skip_perf
	overlay = pyg.surface.Surface(gui.config.overlay_size)
	ups_hist = []
	n_frames = 0
	n_updates = 0
	last_perf_update = 0
	skip_perf = True

	global pyg_font
	pyg.font.init()
	pyg_font = pyg.font.SysFont(gui.config.font, gui.config.font_size)

	render_overlay(0.0, 0.0)
