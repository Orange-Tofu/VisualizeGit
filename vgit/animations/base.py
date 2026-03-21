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
        SPEED_MAP = {'fast': 0.05, 'normal': 0.1, 'slow': 0.3}
        delay = SPEED_MAP.get(getattr(git_state, 'speed', 'normal'), 0.1)
        anim_data = {} # Separate animation-specific state from GitState
        try:
            while True:
                renderable = render_fn(git_state, anim_data)
                if renderable:
                    layout_pane.update(renderable)
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            # Handle cancellation gracefully
            pass


    task = asyncio.create_task(run())
    return AnimationController(task)
