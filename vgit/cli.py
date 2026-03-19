# vgit/cli.py
import click
import asyncio
from vgit import ui
from vgit.commands import status, fetch, commit

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--speed', type=click.Choice(['fast', 'normal', 'slow']), default='normal', help="Animation speed (normal, fast, slow)")
def cli(speed):
    """Educational Git Visualizer"""
    pass

def execute_vgit(cmd_name, git_args):
    ctx = click.get_current_context()
    speed = ctx.parent.params.get('speed', 'normal')
    
    # If the user passed --help, pass it through to git directly
    if '--help' in git_args or '-h' in git_args:
        import subprocess
        full_command = ["git", cmd_name] + list(git_args)
        subprocess.run(full_command)
        return

    mapping = {
        "status": status.run,
        "fetch": fetch.run,
        "commit": commit.run
    }
    
    full_command = ["git", cmd_name] + list(git_args)
    animation_fn = mapping.get(cmd_name, ui.unsupported_command_animation)
    
    asyncio.run(ui.start_ui(animation_fn, full_command, speed))

# Disable individual help for subcommands as per user request
SUBCOMMAND_CONTEXT = dict(ignore_unknown_options=True, help_option_names=[])

@cli.command(name="status", context_settings=SUBCOMMAND_CONTEXT)
@click.argument('git_args', nargs=-1, type=click.UNPROCESSED)
def status_cmd(git_args):
    execute_vgit("status", git_args)

@cli.command(name="fetch", context_settings=SUBCOMMAND_CONTEXT)
@click.argument('git_args', nargs=-1, type=click.UNPROCESSED)
def fetch_cmd(git_args):
    execute_vgit("fetch", git_args)

@cli.command(name="commit", context_settings=SUBCOMMAND_CONTEXT)
@click.argument('git_args', nargs=-1, type=click.UNPROCESSED)
def commit_cmd(git_args):
    execute_vgit("commit", git_args)

def main():
    """Entry point for the console script"""
    cli()

if __name__ == "__main__":
    main()