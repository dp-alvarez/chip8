import itertools
import time
import random
from dataclasses import dataclass, field
from typing import Tuple
import pygame as pyg
from colors import Colors
from cpu import *
from peripherals import *


@dataclass
class Config:
	@dataclass
	class System:
		seed: int = 0
		ramsize: int = 4096
		screen_size: Tuple[int,int] = (64, 32)
		nkeys: int = 16
		delay: float = 1/60
		speed: float = 1/(60*1000*2)

	system: System = field(default_factory=System)
	romfile: str = "roms/chip_modern/danm8ku.ch8"
	screen_size: Tuple[int,int] = (768+1, 384+1)
	screen_pos: Tuple[int,int] = (10, 10)
	overlay_pos: Tuple[int,int] = (10, 405)
	overlay_size: Tuple[int,int] = (780, 185)
	font: str = "Liberation Mono"
	font_size: int = 24
	draw_interval: float = 1/60
	draw_size: int = 12
	draw_color: Colors = Colors.white
	grid_color: Colors = Colors.black
	window_size: Tuple[int,int] = (800, 600)
	window_bg: Colors = Colors.black
	perf_interval: float = 1
	caption: str = "CHIP8 Emu"
	keymap: dict = field(default_factory=lambda: {
		pyg.K_1: 0x1,
		pyg.K_2: 0x2,
		pyg.K_3: 0x3,
		pyg.K_4: 0xc,
		pyg.K_q: 0x4,
		pyg.K_w: 0x5,
		pyg.K_e: 0x6,
		pyg.K_r: 0xd,
		pyg.K_a: 0x7,
		pyg.K_s: 0x8,
		pyg.K_d: 0x9,
		pyg.K_f: 0xe,
		pyg.K_z: 0xa,
		pyg.K_x: 0x0,
		pyg.K_c: 0xb,
		pyg.K_v: 0xf
	})


def update_window():
	# pylint: disable=used-before-assignment, undefined-variable
	global running, last_window_update, n_frames

	if now-last_window_update < config.draw_interval:
		return
	last_window_update = now
	n_frames += 1

	pyg_screen_array[:] = window_bg_mapped
	newscreen = screen.data.repeat(config.draw_size, axis=0).repeat(config.draw_size, axis=1)
	mask = np.zeros(pyg_screen_array.shape, dtype='bool')
	mask[0:newscreen.shape[0], 0:newscreen.shape[1]] = newscreen
	pyg_screen_array[mask] = draw_color_mapped
	pyg.surfarray.blit_array(pyg_screen, pyg_screen_array)

	pyg_window.blit(overlay, config.overlay_pos)
	pyg_window.blit(pyg_screen, config.screen_pos)
	pyg_window.blit(grid, config.screen_pos)
	pyg.display.update()

	pressed = pyg.key.get_pressed()
	for key,code in config.keymap.items():
		keyboard[code] = bool(pressed[key])

	for e in pyg.fastevent.get():
		if e.type == pyg.QUIT:
			running = False


def update_perf_counters():
	# pylint: disable=used-before-assignment
	global last_perf_update, overlay, n_updates, n_frames

	if now-last_perf_update < config.perf_interval:
		return
	last_perf_update = now

	ups = pyg_font.render(f'UPS: {n_updates/config.perf_interval}', False, config.draw_color)
	fps = pyg_font.render(f'FPS: {n_frames/config.perf_interval}', False, config.draw_color)
	overlay.fill(config.window_bg)
	overlay.blit(ups, (0,0))
	overlay.blit(fps, (0,config.font_size))

	n_updates = 0
	n_frames = 0


def create_grid():
	grid = pyg.surface.Surface(config.screen_size)
	grid.set_colorkey(config.window_bg, pyg.RLEACCEL)
	grid.fill(config.window_bg)

	xend = config.draw_size * config.system.screen_size[0]
	yend = config.draw_size * config.system.screen_size[1]
	for i in range(config.system.screen_size[0]+1):
		x = i*config.draw_size
		pyg.draw.line(grid, config.grid_color, (x,0), (x,yend), 1)
	for i in range(config.system.screen_size[1]+1):
		y = i*config.draw_size
		pyg.draw.line(grid, config.grid_color, (0,y), (xend,y), 1)

	return grid


def main():
	global config, running, now, last_window_update, last_perf_update, last_update, n_updates, n_frames
	config = Config()
	running = True
	n_updates = 0
	n_frames = 0
	now = 0
	last_window_update = 0
	last_perf_update = 0
	last_update = 0

	global pyg_window, pyg_screen, pyg_screen_array, pyg_font, grid, overlay
	pyg.display.init()
	pyg.fastevent.init()
	pyg.font.init()
	pyg_window = pyg.display.set_mode(config.window_size)
	pyg.display.set_caption(config.caption)
	pyg_screen = pyg.surface.Surface(config.screen_size)
	pyg_screen_array = pyg.surfarray.array2d(pyg_screen)
	pyg_font = pyg.font.SysFont(config.font, config.font_size)
	grid = create_grid()
	overlay = pyg.surface.Surface(config.overlay_size)

	global draw_color_mapped, window_bg_mapped
	draw_color_mapped = pyg_screen.map_rgb(config.draw_color)
	window_bg_mapped = pyg_screen.map_rgb(config.window_bg)

	global cpu, mem, delay, screen, keyboard, random
	mem = Memory(config.system.ramsize)
	delay = Delay(config.system.delay)
	screen = Screen(config.system.screen_size)
	keyboard = Keyboard(config.system.nkeys)
	random = random.Random(config.system.seed)
	cpu = Cpu(mem, delay, screen, keyboard, random)
	with open(config.romfile, 'rb') as f:
		f.readinto(cpu.mem[cpu.ip:])

	while running:
		if config.system.speed - (time.perf_counter()-last_update) > 0:
			continue

		last_update = time.perf_counter()
		n_updates += 1
		delay.tick(last_update)
		cpu.tick()
		now = time.perf_counter()
		update_perf_counters()
		update_window()

	pyg.quit()


if __name__ == "__main__":
	main()
