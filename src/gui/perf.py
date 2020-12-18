from . import gui
from .window import overlay


def update(now):
	#pylint: disable=used-before-assignment
	global last_update, n_updates, n_frames, skip

	if now-last_update < gui.config.perf_interval:
		return
	last_update = now

	if skip:
		n_frames = 0
		n_updates = 0
		skip = False
		return

	ups = n_updates/gui.config.perf_interval
	fps = n_frames/gui.config.perf_interval
	overlay.render(ups, fps)

	ups_hist.append(n_updates)
	n_updates = 0
	n_frames = 0


def get_average():
	if ups_hist:
		return sum(ups_hist)/(len(ups_hist)*gui.config.perf_interval)
	return 0


def init():
	global ups_hist, n_frames, n_updates, last_update, skip
	ups_hist = []
	n_frames = 0
	n_updates = 0
	last_update = 0
	skip = True
