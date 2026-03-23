import click
import asyncio
from vgit import ui
from vgit.commands import status, fetch, commit

class CatchAllGroup(click.Group):
    """Custom Click Group that intercepts unknown commands and runs them as Git fallbacks."""
    def get_command(self, ctx, cmd_name):
        # Check if the command is explicitly registered (status, fetch, commit)
        cmd = super().get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd
        
        # If not, create a dynamic command that passes everything to execute_vgit
        @click.command(name=cmd_name, context_settings=dict(ignore_unknown_options=True, help_option_names=[]))
        @click.argument('git_args', nargs=-1, type=click.UNPROCESSED)
        def fallback_cmd(git_args):
            execute_vgit(cmd_name, git_args)
        return fallback_cmd

@click.group(
    cls=CatchAllGroup,
    context_settings=dict(help_option_names=['-h', '--help']),
    invoke_without_command=True
)
@click.option('--speed', type=click.Choice(['fast', 'normal', 'slow']), default='normal', help="Animation speed (normal, fast, slow)")
@click.pass_context
def cli(ctx, speed):
    """Educational Git Visualizer — Animations loop until keypress."""
    if ctx.invoked_subcommand is None:
        # User entered 'vgit' with no args - show help
        click.echo(cli.get_help(ctx))

def execute_vgit(cmd_name, git_args):
    ctx = click.get_current_context()
    # Speed might be in current context (fallback case) or parent context (subcommand case)
    speed = ctx.params.get('speed')
    if speed is None and ctx.parent:
        speed = ctx.parent.params.get('speed')
    if speed is None:
        speed = 'normal'
    
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