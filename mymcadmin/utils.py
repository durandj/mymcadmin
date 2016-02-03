import logging

def setup_logging():
	# TODO(durandj): make log level changeable
	# TODO(durandj): make log format customizable
	logging.basicConfig(
		datefmt = '',
		format  = '',
		level   = logging.INFO,
	)

