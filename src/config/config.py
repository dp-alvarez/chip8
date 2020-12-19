import pygame as pyg
from dataclasses import dataclass, field
from .window import WindowConfig
from .system import SystemConfig


@dataclass
class Config:
	system: SystemConfig = field(default_factory=SystemConfig)
	window: WindowConfig = None
	romfile: str = "roms/chip_modern/danm8ku.ch8"
	perf_interval: float = 1
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

	def __post_init__(self):
		if not self.window:
			self.window = WindowConfig(sysconfig=self.system)
