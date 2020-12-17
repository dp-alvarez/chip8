"""@todo
talvez sub-pacotes em emulator
separar perhiperals
serparar configs em package

better rom loading
parsing command line
comentar codigo

comando de wait key tem que esperar key ser apertada mesmo se ja tiver uma apertada

usar o cache do functools da um ganho de performance de mais de 2x
trocar opcode pra calculo estatico dos parametros x, y, nn, nnn
implementar som
lookup via tabela
criar scheduler, tem um na stdlib
"""


import time
import random
from dataclasses import dataclass, field
import pygame as pyg
from emulator import *
from gui import *


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


def tick_emulator():
	try:
		delay.tick(now)
		cpu.tick()
	except EmulationError as e:
		handle_emulation_error(e)


def handle_emulation_error(e):
	print(f'{type(e).__name__}: {e}')
	print(cpu)
	# cmd = input()
	cmd = "r"
	overlay.skip_perf = True

	if cmd == "q":
		raise WindowClose

	elif cmd == "c":
		cpu.ip += cpu.opc.size

	elif cmd == "r":
		raise e

	else:
		raise e


def main():
	global config, now
	config = Config()
	now = 0
	last_update = 0

	global cpu, mem, delay, screen, keyboard, random
	mem = Memory(config.system.ramsize)
	delay = Delay(config.system.delay)
	screen = Screen(config.system.screen_size)
	keyboard = Keyboard(range(len(config.keymap)))
	random = random.Random(config.system.seed)
	cpu = Cpu(mem, delay, screen, keyboard, random)

	with open(config.romfile, 'rb') as f:
		f.readinto(cpu.mem[cpu.ip:])

	gui_init(config, screen, keyboard)

	try:
		while True:
			while now-last_update < config.system.speed:
				now = time.perf_counter()
			last_update = now
			overlay.n_updates += 1
			tick_emulator()
			overlay.update_overlay(now)
			update_window(now)

	except WindowClose:
		pass

	finally:
		print(f"Avg UPS: {overlay.get_average():,.0f}")
		gui_quit()


if __name__ == "__main__":
	main()
