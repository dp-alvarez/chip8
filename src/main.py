"""@todo
better rom loading
parsing command line
separar main em arquivos ou package
comentar codigo

comando de wait key tem que esperar key ser apertada mesmo se ja tiver uma apertada

trocar opcode pra calculo estatico dos parametros x, y, nn, nnn
implementar som
lookup via tabela
"""


import time
import random
from dataclasses import dataclass, field
import pygame as pyg
import numpy as np
from emulator import *
from colors import Colors


@dataclass
class Config:
	@dataclass
	class System:
		speed: float = 1/(60*1000*1000)
		delay: float = 1/60
		seed: int = 0
		screen_size: tuple[int,int] = (64, 32)
		ramsize: int = 4096

	system: System = field(default_factory=System)
	romfile: str = "roms/chip_modern/danm8ku.ch8"
	draw_interval: float = 1/60
	perf_interval: float = 1
	draw_size: int = 12
	margin: int = 10
	font_size: int = 24
	font: str = "Liberation Mono"
	screen_size: tuple[int,int] = (System.screen_size[0]*draw_size+1, System.screen_size[1]*draw_size+1)
	screen_pos: tuple[int,int] = (margin, margin)
	overlay_size: tuple[int,int] = (screen_size[0], 2*font_size)
	overlay_pos: tuple[int,int] = (screen_pos[0], 2*margin+screen_size[1])
	window_size: tuple[int,int] = (2*margin+max(screen_size[0],overlay_size[0]), 3*margin+screen_size[1]+overlay_size[1])
	draw_color: Colors = Colors.white
	grid_color: Colors = Colors.black
	window_bg: Colors = Colors.black
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

	pyg_screen_array[:] = config.window_bg_mapped
	newscreen = np.array(screen.data, dtype='bool', copy=False).reshape(screen.shape)
	newscreen = newscreen.repeat(config.draw_size, axis=0).repeat(config.draw_size, axis=1)
	mask = np.zeros(pyg_screen_array.shape, dtype='bool')
	mask[0:newscreen.shape[0], 0:newscreen.shape[1]] = newscreen
	pyg_screen_array[mask] = config.draw_color_mapped
	pyg.surfarray.blit_array(pyg_screen, pyg_screen_array)

	pyg_window.blit(overlay, config.overlay_pos)
	pyg_window.blit(pyg_screen, config.screen_pos)
	pyg_window.blit(grid, config.screen_pos)
	pyg.display.update()

	pressed = pyg.key.get_pressed()
	for key,button in config.keymap.items():
		keyboard[button] = bool(pressed[key])

	for e in pyg.fastevent.get():
		if e.type == pyg.QUIT:
			running = False


def update_perf_counters():
	# pylint: disable=used-before-assignment
	global last_perf_update, n_updates, n_frames, skip_perf

	if now-last_perf_update < config.perf_interval:
		return
	last_perf_update = now

	if skip_perf:
		n_frames = 0
		n_updates = 0
		skip_perf = False
		return

	ups = f'UPS: {n_updates/config.perf_interval:,.0f}'
	fps = f'FPS: {n_frames/config.perf_interval:,}'
	ups = pyg_font.render(ups, False, config.draw_color)
	fps = pyg_font.render(fps, False, config.draw_color)
	overlay.fill(config.window_bg)
	overlay.blit(ups, (0,0))
	overlay.blit(fps, (0,config.font_size))

	ups_hist.append(n_updates)
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


def tick_emulator():
	try:
		delay.tick(now)
		cpu.tick()
	except EmulationError as e:
		handle_emulation_error(e)


def handle_emulation_error(e):
	global cpu, running, skip_perf

	print(f'{type(e).__name__}: {e}')
	print(cpu)
	# cmd = input()
	cmd = "r"
	skip_perf = True

	if cmd == "q":
		running = False

	elif cmd == "c":
		cpu.ip += cpu.opc.size

	elif cmd == "r":
		raise e

	else:
		raise e


def main():
	global config, running, now, last_update, last_window_update, last_perf_update, n_updates, n_frames, ups_hist, skip_perf
	config = Config()
	running = True
	now = 0
	n_updates = 0
	n_frames = 0
	skip_perf = False
	last_window_update = 0
	last_perf_update = 0
	last_update = 0
	ups_hist = []

	global pyg_window, pyg_screen, pyg_screen_array, pyg_font, grid, overlay
	pyg.display.init()
	pyg.fastevent.init()
	pyg.font.init()
	pyg_window = pyg.display.set_mode(config.window_size)
	pyg.display.set_caption(config.caption)
	pyg_screen = pyg.surface.Surface(config.screen_size)
	pyg_screen_array = pyg.surfarray.array2d(pyg_screen)
	config.draw_color_mapped = pyg_screen.map_rgb(config.draw_color)
	config.window_bg_mapped = pyg_screen.map_rgb(config.window_bg)
	grid = create_grid()
	overlay = pyg.surface.Surface(config.overlay_size)
	pyg_font = pyg.font.SysFont(config.font, config.font_size)

	now = time.perf_counter()
	pyg_window.fill(config.window_bg)
	update_perf_counters()
	ups_hist.clear()

	global cpu, mem, delay, screen, keyboard, random
	mem = Memory(config.system.ramsize)
	delay = Delay(config.system.delay)
	screen = Screen(config.system.screen_size)
	keyboard = Keyboard(range(len(config.keymap)))
	random = random.Random(config.system.seed)
	cpu = Cpu(mem, delay, screen, keyboard, random)

	with open(config.romfile, 'rb') as f:
		f.readinto(cpu.mem[cpu.ip:])

	last_perf_update = time.perf_counter()
	try:
		while running:
			while now-last_update < config.system.speed:
				now = time.perf_counter()
			last_update = now
			n_updates += 1
			tick_emulator()
			update_perf_counters()
			update_window()

	finally:
		if ups_hist:
			avg_ups = sum(ups_hist)/(len(ups_hist)*config.perf_interval)
			print(f"Avg UPS: {avg_ups:,.0f}")
		pyg.quit()


if __name__ == "__main__":
	main()
