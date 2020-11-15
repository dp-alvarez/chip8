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
		speed: float = 1/(60*30)

	system: System = field(default_factory=System)
	romfile: str = "roms/chip_games/pong.ch8"
	# romfile: str = "roms/octo_examples/keyboard.ch8"
	# romfile: str = "roms/octo_examples/default/compiled.ch8"
	busy_amount: float = 1/10
	screen_size: Tuple[int,int] = (768+1, 384+1)
	screen_pos: Tuple[int,int] = (10, 10)
	screen_bg: Colors = Colors.black
	draw_interval: float = 1/60
	draw_size: int = 12
	draw_color: Colors = Colors.white
	grid_color: Colors = Colors.gray
	window_size: Tuple[int,int] = (800, 600)
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


def draw():
	# pylint: disable=used-before-assignment
	global last_draw

	if last_draw is not None and now-last_draw < config.draw_interval:
		return
	last_draw = now

	pyg_screen.fill(config.screen_bg)
	for x,y in screen:
		if screen[x,y]:
			pyg.draw.rect(pyg_screen, config.draw_color, ((x*config.draw_size,y*config.draw_size), (config.draw_size,config.draw_size)), 0)

	pyg_window.blit(pyg_screen, config.screen_pos)
	pyg_window.blit(grid, config.screen_pos)
	pyg.display.update()


def read_input():
	global running

	pressed = pyg.key.get_pressed()
	for key,code in config.keymap.items():
		keyboard[code] = bool(pressed[key])

	for e in pyg.fastevent.get():
		if e.type == pyg.QUIT:
			running = False


def create_grid():
	color = config.grid_color
	bg = Colors.black if color is not Colors.black else Colors.white
	grid = pyg.surface.Surface(config.screen_size)
	grid.set_colorkey(bg, pyg.RLEACCEL)
	grid.fill(bg)

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
	global config, running, now, last_draw, last_update
	config = Config()
	running = True
	now = 0
	last_draw = None
	last_update = None

	global pyg_window, pyg_screen, grid
	pyg.display.init()
	pyg.fastevent.init()
	pyg_window = pyg.display.set_mode(config.window_size)
	pyg.display.set_caption(config.caption)
	pyg_screen = pyg.surface.Surface(config.screen_size)
	grid = create_grid()

	global cpu, mem, delay, screen, keyboard, random
	mem = Memory(config.system.ramsize)
	delay = Delay(config.system.delay)
	screen = Screen(config.system.screen_size)
	keyboard = Keyboard(config.system.nkeys)
	random = random.Random(config.system.seed)
	cpu = Cpu(mem, delay, screen, keyboard, random)
	with open(config.romfile, 'rb') as f:
		f.readinto(cpu.mem[cpu.ip:])

	last_update = time.perf_counter()
	while running:
		now = time.perf_counter()
		tosleep = config.busy_amount * (config.system.speed - (now-last_update))
		if tosleep >= 0:
			time.sleep(tosleep)
		else:
			last_update = now
			read_input()
			delay.tick(now)
			cpu.tick()
			draw()

	pyg.quit()


if __name__ == "__main__":
	main()
