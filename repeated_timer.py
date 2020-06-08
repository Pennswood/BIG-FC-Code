"""
Taken from:
https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds#474543
Allows for a timer to be set every _interval_ seconds to execute a function.
"""
from threading import Timer

class RepeatedTimer():
	"""RepeatedTimer calls a function every _interval_ seconds until stop() is called."""
	def __init__(self, interval, function, *args, **kwargs):
		self._timer = None
		self.interval = interval
		self.function = function
		self.args = args
		self.kwargs = kwargs
		self.is_running = False
		self.start()

	def _run(self):
		self.is_running = False
		self.start()
		self.function(*self.args, **self.kwargs)

	def start(self):
		"""Starts running _function_ every _interval_ seconds. Can be stopped with stop()"""
		if not self.is_running:
			self._timer = Timer(self.interval, self._run)
			self._timer.start()
			self.is_running = True

	def stop(self):
		"""Stops running the timer. Can be started again with start()"""
		self._timer.cancel()
		self.is_running = False
