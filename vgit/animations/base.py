# animations/base.py
import asyncio

class AnimationController:
    def __init__(self, task):
        self._task = task

    async def stop(self):
        """Stop the animation by cancelling the task."""
        if not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

def start_animation(layout_pane, render_fn, git_state):
    """
    Start the animation loop as an asyncio Task.
    """
    async def run():
        try:
            while True:
                # render_fn now returns a rich renderable (e.g. Panel, Group, Table)
                renderable = render_fn(git_state)
                if renderable:
                    layout_pane.update(renderable)
                await asyncio.sleep(0.1)  # Faster frame rate for smoother animation
        except asyncio.CancelledError:
            # Handle cancellation gracefully
            pass

    task = asyncio.create_task(run())
    return AnimationController(task)
