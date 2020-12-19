import re
from .exceptions import *
from .opcode import Opcode
from . import opcode_handlers, char_data


class Cpu:
	char_data = char_data.char_data
	opcode_handlers = opcode_handlers.opcode_handlers

	def __init__(self, mem, delay, screen, keyboard, random):
		self.mem = mem
		self.delay = delay
		self.screen = screen
		self.keyboard = keyboard
		self.random = random
		self.stack = []
		self.ip = 0x200
		self.v = [0] * 16
		self.i = 0
		self.keyboard_old = None
		self.init_opcode_handlers()
		self.init_chars()

	def init_opcode_handlers(self):
		# pylint: disable=assignment-from-no-return
		self.opcode_handlers = dict()
		for regex,opcode in Cpu.opcode_handlers.items():
			self.opcode_handlers[re.compile(regex)] = opcode.__get__(self, self.__class__)

	def init_chars(self):
		pos = 0
		self.char_pos = {}
		for char, data in self.char_data.items():
			data = bytes(data)
			datalen = len(data)
			pos += datalen
			self.char_pos[char] = pos
			self.mem[pos:pos+len(data)] = data

	def opcode_lookup(self, opcode_str):
		for regex in self.opcode_handlers:
			if regex.fullmatch(opcode_str):
				return self.opcode_handlers[regex]
		raise InvalidOpcodeError(f"No handler for opcode: {opcode_str}")

	def tick(self):
		try:
			self.opc = Opcode(self.mem[self.ip:])
			opcode_handler = self.opcode_lookup(self.opc.hex())
			opcode_handler()
		except EmulationError:
			raise
		except Exception as e:
			raise EmulationError(e) from e

	def __str__(self):
		ret = ""
		for i,x in enumerate(self.v):
			ret += f"{i:01X}: 0x{x:02X}"
			ret += "    " if (i+1)%4 else "\n"
		ret += f"I:  0x{self.i:04X} -"
		for addr in range(self.i, self.i+4):
			ret += f" {self.mem[addr]:02x}" if addr < len(self.mem) else " XX"
		ret += "\n"
		ret += f"IP: 0x{self.ip:04X} - {self.opc}\n"
		ret += f"Delay: {self.delay}\n"
		ret += f"Stack: {str(self.stack)}\n"
		return ret
