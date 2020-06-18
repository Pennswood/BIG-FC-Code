"""
Logging, saving spectrometer samples
If you need to save a file please use/call functions here

Basic file hierarchy for Oasis:

	OASIS_SD_PATH/		(This is all on the SD card)
		* logs/
			* [All of our status logs] 0.statlog, 1.statlog, 2.statlog, 3.statlog...
		* samples/
			* [All of our spectrometer samples] file extension: .bin
			* Spectrometer samples are named using the UNIX timestamp they were taken at as well as the fractional amount of seconds (just pass in time.time(), don't cast to an int)
		* debug/
			* [Any debug logs generated, probably unused]

	OASIS_FLASH_PATH/	(This is all on the flash memory)
		* To be decided...

manifest.log format
	Each line in manifest.log corresponds to the number of .dat file (For example, the first line corresponds to file 0.dat, second line corresponds to 1.dat, fourth line corresponds to 3.dat...)

	Each line contains the UNIX timestamp that the sample was taken at

	The order that samples occured in can be deduced through a combination of the file #, and the UNIX timestamp. This means that if two files have the same timestamp, the file with a lower file # was taken first.
"""

#TODO: Does list_all_samples and list_all_logs need to be reverse sorted so most recent is at the head of the array?

import pickle
import os
import time
import oasis_config
import unireedsolomon as rs
from pathlib import Path
import struct

from oasis_config import LOGS_PER_FILE, STATUS_SIZE

class FileManager():

	def save_sample(self, timestamp, data):
		"""
		After the spectrometer finishes sampling, it will send the data to this function to be saved.
		
		Parameters
		----------
		timestamp : string
			A string of current linux time to be formatted [timestamp].[file extension]
		data : array
			A 2 by 3648 data array containing the recorded data from the spectrometer (wavelength, intensity)

		"""
		# TODO: other numbers for failure to save file (for debugging purposes)
		file_name = str(timestamp).replace(".","_") + ".bin" # Get the filename from the timestamp and extension
		f = (self.samples_directory_path / file_name).open("wb")
		for i in range(len(data)):
			for j in range(len(data[i])):
				data[i][j] = bytes(struct.pack("f",data[i][j]))
				f.write(data)
		#pickle.dump(data, f) # This writes the data
		f.close()
		return

	def read_sample(self, timestamp):
		"""
		Returns the data array of the specific file.

		Parameters
		----------
		time : string
			Specific file name for an array of spectrometer data at a certain time. This will be formatted as [name].[file extension]

		Returns
		-------
		data : array
			A 2 by 3648 data array from the spectrometer (wavelength, intensity)
		"""
		file_name = str(timestamp).replace(",","_") + ".bin"
		f = (self.samples_directory_path / file_name).open("rb")
		output = [[],[]]
		for x in range(oasis_config.SPECTROMETER_PIXEL_NUMBER):
			output[0].append(struct.unpack("f",f.read(4)))
		for x in range(oasis_config.SPECTROMETER_PIXEL_NUMBER):
			output[1].append(struct.unpack("f",f.read(4)))
		return output

	def get_last_two_samples(self):
		"""
		Returns the two string of the last 2 spectrometer sample files.

		Returns
		-------
		array
			This will be a 2x1 string array containing the data of the last two spectrometer sample files. The first string being the most recent followed by the second string being the second most recent
				* Array format: {[most recent file name].[file extension], [next recent file name].[file extension]}
				* If less than 2 files exist, then the second (and possibly the first) string will be left an empty string
		"""
		l = sorted(self.samples_directory_path.glob("*.bin"), reverse=True)
		if len(l) == 0:
			return [None] * 2
		elif len(l) == 1:
			l.append(None) # Just shove a None to the end

		return l[0:2] # return the most recent, and next oldest spectrometer file paths, in that order

	def list_all_samples(self):
		"""
		Returns strings of all spectrometer sample files.

		Returns
		-------
		sample_files : array
			A nx1 string array of all n spectrometer files sorted from most recent to least recent.
				* The array will be in the format: {[most recent file name].[file extension], [next recent file name].[file extension], ...}
		"""
		return sorted(self.samples_directory_path.glob("*.bin"))

	def list_all_logs(self):
		"""
		Returns all log files in an array.

		Returns
		-------
		log_files : array
			An array composed of every log file saved on Oasis' sd card
				* The array will be in the format: {[most recent file], [next most recent file], ...}
		"""
		return sorted(self.log_directory_path.glob("*.statlog"))

	def get_latest_log_file(self):
		"""
		Returns most recent log file.
		
		Returns
		-------
		log_file : string
			A string of the file name for the most recent log file recorded.
		"""
		l = sorted(self.log_directory_path.glob("*.statlog"), reverse=True)
		if len(l) == 0:
			return None
		return l[0]


	def log_status(self, status_array, log_reason=0):
		"""
		Append data into the log file. May automatically create a new file.
		Inputs: Bit string data to input.

		Parameters
		----------
		status_array : array
			This is a byte array of status data
		log_reason : int
			0 = regular time log, 1 = command sent, 2 = new error, 3 = error resolved

		Returns
		-------
		number : int
			0 = success. Another number = failure to save file (for debugging purposes)
		"""
		global STATUS_SIZE, LOGS_PER_FILE
		data = int(time.time()).to_bytes(4, byteorder="big", signed=True)
		data += status_array
		data += log_reason.to_bytes(1, byteorder="big", signed=False)
		self.log_file.write(data)

		if self.current_log_file_path.stat().st_size > LOGS_PER_FILE * STATUS_SIZE:
			self.log_index += 1
			self.current_log_file_path = self.log_directory_path / (str(self.log_index) + ".statlog")
			self.log_file.close()
			self.log_file = self.current_log_file_path.open("ab", buffering=STATUS_SIZE)

	def __init__(self, sd_path, flash_path):
		self.sd_path = sd_path
		if not sd_path.exists():
			print("WARNING: SD_PATH " + str(sd_path) + " does not exist! Attempting to create...")
			try:
				sd_path.mkdir(parents=True)
			except:
				print("ERROR: Failed to create SD_PATH directory " + str(sd_path))

		if not sd_path.is_dir():
			print("ERROR: SD_PATH " + str(sd_path) + " is not a directory! Did you forget to mount or insert the SD card?")
			# TODO: Switch over to flash only

		self.flash_path = flash_path
		if not flash_path.exists():
			print("WARNING: FLASH_PATH " + str(flash_path) + " does not exist! Attempting to create...")
			try:
				flash_path.mkdir(parents=True)
			except:
				print("ERROR: Failed to create FLASH_PATH directory " + str(flash_path))

		if not flash_path.is_dir():
			print("ERROR: FLASH_PATH " + str(flash_path) + " is not a directory!")
			# TODO: Uh oh, this is like super bad... how do we even respond to this?

		# Set up the paths to the directories we will be working with
		self.samples_directory_path = self.sd_path / "samples/"
		if not self.samples_directory_path.exists():
			print("WARNING: Samples directory " + str(self.samples_directory_path) + " does not exist! Attempting to create...")
			try:
				self.samples_directory_path.mkdir()
			except:
				print("ERROR: Failed to create samples directory " + str(self.samples_directory_path))


		self.log_directory_path = self.sd_path / "logs/"
		if not self.log_directory_path.exists():
			print("WARNING: Log directory " + str(self.log_directory_path) + " does not exist! Attempting to create...")
			try:
				self.log_directory_path.mkdir()
			except:
				print("ERROR: Failed to create log directory " + str(self.log_directory_path))


		self.debug_directory_path = self.sd_path / "debug/"
		if not self.debug_directory_path.exists():
			print("WARNING: debug directory " + str(self.debug_directory_path) + " does not exist! Attempting to create...")
			try:
				self.debug_directory_path.mkdir()
			except:
				print("ERROR: Failed to create debug directory " + str(self.debug_directory_path))


		# Set up our logging file handles
		self.current_log_file_path = self.get_latest_log_file()
		if self.current_log_file_path == None: # this is the first log file to be opened, bootstrap the process
			self.log_index = 0
			self.current_log_file_path = self.log_directory_path / "0.statlog"
		else: # first log file already exists, check to see if the most recent log file is still usable
			self.log_index = int(self.current_log_file_path.name[:-len(".statlog")])

			if self.current_log_file_path.stat().st_size > LOGS_PER_FILE * STATUS_SIZE:
				self.log_index += 1
				self.current_log_file_path = self.log_directory_path / (str(self.log_index) + ".statlog")

		self.log_file = self.current_log_file_path.open("ab", buffering=STATUS_SIZE)

		print("INFO: FileManager initialized.")
