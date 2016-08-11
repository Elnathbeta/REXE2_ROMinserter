#!/usr/bin/env python3
# coding=utf-8
# This module is a small wrapper for the standard logging module.
# It is intended for setting up logging in no time.
# Just create a Logger object and start logging!
#
# Copyright (C) 2016 Elnath < elnathbeta@gmail.com >
#
# Licensed under the MIT license:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of (the) Author shall not be used in advertising or
# otherwise to promote the sale, use or other dealings in this Software without
# prior written authorization from (the)Author.
import logging
import logging.handlers
import sys

# HANDLER CONSTANTS
# This constants are used to define which handler are enabled for a specific logger.
# They are flags: you can combine them with a bitwise or
HANDLER_NONE = 0
HANDLER_STDOUT = 1
HANDLER_STDERR = 2
HANDLER_FILE = 4
HANDLER_ALL = 7

class Logger():
	"""
		Objects of this class are used for logging.
		You should create one for every module for which you wish to have logging.
	"""
	def __init__(self, name, level = "info", handlers_enabled = HANDLER_STDOUT|HANDLER_STDERR, **options):
		"""
		A logger capable to output its messages to different handlers.

		:param name: The name of the logger as required for the :mod:`logging` module.
			Normally you can use `__name__` as it will be the name of the module that creates the logger.
			It is not possible to create two logger with the same :attr:`name` attribute
		:param level: Minimum level of the logger. Valid values are "debug", "info", "warning", "error", "critical".
		:param handlers_enabled: handlers that will be enabled for logging. This is a combination of flags constants defined in the module namespace.
			This is intended so when you want to enable/disable a handler you just need to remove a flag: you don't need to modofy the `options`

			Valid values are:

			- HANDLER_STDOUT
			- HANDLER_STDERR
			- HANDLER_FILE : a WatchedFileHandler or RotatingFileHandler
		:param **options: Options for all the handlers. If an option is missing, default value will be used.
			For a list of options and defaults values look at the source code (beginning of :func:`__init__` function)
		"""
		default_options = {
			# Valid values for levels are: "debug", "info", "warning", "error", "critical", None(no limit)
			# Minimum levels are inclusive, maximum level are exclusive (that means that a maximum level of 'warning' will only log messages up to 'info')
			# Formats: see logging module documentation
			"stdout_minLevel": "debug",
			"stdout_maxLevel": "warning",
			"stdout_format": "=> %(asctime)s ["+name+"][%(levelname)s] %(message)s", #Add %(threadName)s for the name of the tread that logged the message
			"stdout_dateformat": "%Y-%m-%d(%a) %H:%M:%S", # Only useful if %(asctime)s is present in the log format
			"stderr_minLevel": "warning",
			"stderr_maxLevel": None,
			"stderr_format": "=> %(asctime)s ["+name+"][%(levelname)s] %(message)s",
			"stderr_dateformat": "%Y-%m-%d(%a) %H:%M:%S",
			"file_name": name+".log",
			"file_mode": "a", # Opening mode for the file
			"file_encoding": "utf-8",
			"file_delay": True, #If true, file opening is deferred until the first message is logged
			"file_rotating": True, #If true, a RotatingFileHandler is used: when the file reach a certain size a new one will be created and the old one will be renamed to a backup name
			"file_maxBytes": 5*1000, # When the file exceeds this size the log will rotate. Ignored if file_rotating is False.
			"file_backupCount": 3, # How many backup log keep at every time. Ignored if file_rotating is False.
			"file_minLevel": "debug",
			"file_maxLevel": None,
			"file_format": "=> %(asctime)s ["+name+"][%(levelname)s] %(message)s",
			"file_dateformat": "%Y-%m-%d(%a) %H:%M:%S",
		}

		default_options.update(options)
		options = default_options
		self.Logger = logging.getLogger(name)
		self.Logger.setLevel(self.level_from_string(level))

		if (handlers_enabled & HANDLER_STDOUT):
			handler = logging.StreamHandler(sys.stdout)
			handler.setFormatter(logging.Formatter(options["stdout_format"], datefmt =options["stdout_dateformat"]))
			if options["stdout_minLevel"] != None:
				handler.setLevel(self.level_from_string(options["stdout_minLevel"]))
			if options["stdout_maxLevel"] != None:
				handler.addFilter(_MaxLevelFilter(self.level_from_string(options["stdout_maxLevel"])))
			self.Logger.addHandler(handler)
		if (handlers_enabled & HANDLER_STDERR):
			handler = logging.StreamHandler(sys.stderr)
			handler.setFormatter(logging.Formatter(options["stderr_format"], datefmt =options["stderr_dateformat"]))
			if options["stderr_minLevel"] != None:
				handler.setLevel(self.level_from_string(options["stderr_minLevel"]))
			if options["stderr_maxLevel"] != None:
				handler.addFilter(_MaxLevelFilter(self.level_from_string(options["stderr_maxLevel"])))
			self.Logger.addHandler(handler)
		if (handlers_enabled & HANDLER_FILE):
			kwargs = {
				"mode": options["file_mode"],
				"encoding": options["file_encoding"],
				"delay": options["file_delay"],
			}
			if options["file_rotating"]:
				kwargs["maxBytes"] = options["file_maxBytes"]
				kwargs["backupCount"] = options["file_backupCount"]
				handler = logging.handlers.RotatingFileHandler(options["file_name"], **kwargs)
			else:
				handler = logging.handlers.WatchedFileHandler(options["file_name"], **kwargs)

			handler.setFormatter(logging.Formatter(options["file_format"], datefmt = options["file_dateformat"]))
			if options["file_minLevel"] != None:
				handler.setLevel(self.level_from_string(options["file_minLevel"]))
			if options["file_maxLevel"] != None:
				handler.addFilter(_MaxLevelFilter(self.level_from_string(options["file_maxLevel"])))
			self.Logger.addHandler(handler)

	@staticmethod
	def level_from_string(s):
		"""
		Convert a string representing a logging level to a level from :mod:`logging` module.

		Accepted values are "debug", "info", "warning", "error", "critical".
		"""
		if s == "debug" :
			return logging.DEBUG
		elif s == "info":
			return logging.INFO
		elif s == "warning":
			return logging.WARNING
		elif s == "error":
			return logging.ERROR
		elif s == "critical":
			return logging.CRITICAL
		else:
			return logging.NOTSET


	def log(self, level, message, *args, **kwargs):
		"""
			Log a message.

			:param level: The message level. Valid values are "debug", "info", "warning", "error", "critical".
			:param message: The message to log.
			:param *args: See :func:`logging.Logger.log` documentation.
			:param **kwargs: See :func:`logging.Logger.log` documentation.
		"""
		self.Logger.log(self.level_from_string(level), message, *args, **kwargs)

	def debug(self, message, *args, **kwargs):
		"""
			Shorthand method for `log("debug", message, *args, **kwargs)`
		"""
		self.log("debug", message, *args, **kwargs)

	def info(self, message, *args, **kwargs):
		"""
			Shorthand method for `log("info", message, *args, **kwargs)`
		"""
		self.log("info", message, *args, **kwargs)

	def warning(self, message, *args, **kwargs):
		"""
			Shorthand method for `log("warning", message, *args, **kwargs)`
		"""
		self.log("warning", message, *args, **kwargs)

	def error(self, message, *args, **kwargs):
		"""
			Shorthand method for `log("error", message, *args, **kwargs)`
		"""
		self.log("error", message, *args, **kwargs)

	def critical(self, message, *args, **kwargs):
		"""
			Shorthand method for `log("critical", message, *args, **kwargs)`
		"""
		self.log("critical", message, *args, **kwargs)

class _MaxLevelFilter():
	"""
		Allows only messages with level < Level attribute. Note that it is 'strictly lower', because logger.setLevel is inclusive.
	"""
	def __init__(self, level):
		self.Level = level
	def filter(self, record):
		"""
			Process the event.
			:return: True if the event should be logged, False otherwise
		"""
		return record.levelno < self.Level

if __name__ == '__main__':
	#Example of utilisation
	logger = Logger(__name__, "debug", HANDLER_ALL, stdout_minLevel = "info", file_name = "logmoduleTest.log")
	logger.debug("debug")
	logger.info("info")
	logger.warning("warning")
	logger.error("error")
	logger.critical("critical")
