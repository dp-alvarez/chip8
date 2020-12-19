"""@todo
better rom loading
parsing command line
comentar codigo

talvez criar sub-module pra cpu e opcodes
implementar som
usar o cache do functools da um ganho de performance de mais de 2x
trocar opcode pra calculo estatico dos parametros x, y, nn, nnn
lookup via tabela
criar scheduler, tem um na stdlib
"""


import time
import random
from config import *
from emulator import *
from gui import *


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
	perf.skip = True

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
	sysconfig = SystemConfig(
		speed = 1/(1000000*100)
	)
	winconfig = WindowConfig(sysconfig=sysconfig)
	config = Config(system=sysconfig, window=winconfig)
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

	init(config, screen, keyboard)

	try:
		while True:
			while now-last_update < config.system.speed:
				now = time.perf_counter()
			last_update = now
			perf.n_updates += 1
			tick_emulator()
			perf.update(now)
			window.update(now)

	except WindowClose:
		pass

	finally:
		print(f"Avg UPS: {perf.get_average():,.0f}")
		gui_quit()


if __name__ == "__main__":
	main()
