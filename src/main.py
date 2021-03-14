import time
import random
import sys
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
	cmd = input()
	perf.skip = True

	if cmd == "q":
		raise WindowClose

	elif cmd == "c":
		cpu.ip += cpu.opc.size

	elif cmd == "r":
		raise e

	else:
		raise e


def main(romfile, speed):
	global config, now
	sysconfig = SystemConfig(speed=speed)
	winconfig = WindowConfig(sysconfig=sysconfig)
	config = Config(system=sysconfig, window=winconfig, romfile=romfile)
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
		print(f"Avg UPS: {perf.get_average():,.0f}")

	finally:
		gui_quit()


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: chip8_emu <rom file> <emulation speed>")
		sys.exit(1)
	else:
		romfile = sys.argv[1]
		speed = 1/(1000000)
		if len(sys.argv) >= 3:
			speed = 1/int(sys.argv[2])

	main(romfile, speed)
