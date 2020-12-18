class Delay:
	def __init__(self, freq):
		self.freq = freq
		self.data = 0
		self.last_update = None

	def set(self, value):
		self.data = value

	def get(self):
		return self.data

	def tick(self, time):
		if self.last_update is None or time-self.last_update >= self.freq:
			if self.data > 0:
				self.data -= 1
			self.last_update = time

	def __str__(self):
		return str(self.data)
