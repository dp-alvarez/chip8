from dataclasses import dataclass


@dataclass
class SystemConfig:
	speed: float = 1/(60*1000)
	delay: float = 1/60
	seed: int = 0
	screen_size: tuple[int,int] = (64, 32)
	ramsize: int = 4096
