import click
import functools
import os.path
import subprocess
import sys

from . import internal, params
from .. import config, server
from .base import mymcadmin

def uses_internal(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		return func(sys.argv[0], *args, **kwargs)

	return wrapper

def run_process(cmd, success_msg, error_msg):
	proc = subprocess.Popen(cmd)
	proc.wait()

	if proc.returncode == 0:
		click.echo(click.style(success_msg, fg = 'green'))
	else:
		click.echo(click.style(error_msg, fg = 'red'))

@mymcadmin.command()
@click.pass_context
def list(ctx):
	"""
	List all of the available servers
	"""

	click.echo(click.style('Available servers:', fg = 'blue'))
	for srv in server.Server.list_all(ctx.obj['config']):
		click.echo(os.path.basename(srv))

@mymcadmin.command()
@click.pass_context
@uses_internal
@click.argument('server', type = params.ServerParamType())
def start(script, ctx, server):
	"""
	Start a Minecraft server
	"""

	run_process(
		[script, 'internal', 'start', server.name],
		'Server is starting',
		'Error occurred while starting the server',
	)

@mymcadmin.command()
@click.pass_context
@uses_internal
@click.argument('server', type = params.ServerParamType())
def stop(script, ctx, server):
	"""
	Stop a Minecraft server
	"""

	server.stop()
	click.echo(click.style('Stopping server', fg = 'green'))

@mymcadmin.command()
@click.pass_context
@uses_internal
@click.argument('server', type = params.ServerParamType())
def restart(script, ctx, server):
	"""
	Restart a Minecraft server
	"""

	run_process(
		[script, 'internal', 'restart', server.name],
		'Restarting the server',
		'Error occurred while restarting the server',
	)

