# Animation Design Standards

To ensure a consistent user experience across different Git command animations in `vgit`, follow these UI patterns:

## Continuous Looping Pattern
Animations should not remain static after completion. Instead, they should:
1.  Play the main sequence.
2.  Pause at the "Done" state for 2-3 seconds.
3.  Display a "Restarting animation..." indicator.
4.  Reset to the first frame and repeat.

## Feedback Messaging
When an animation is in the pause/done state and about to restart, the UI should be consistent:

- **Main Note**: Explains the result of the command (e.g., "New commit added!", "Fetched 2 commits").
- **Restarting Notice**:
    - **Text**: `Restarting animation...`
    - **Style**: `dim italic` (Grey/low prominence).
    - **Position**: Bottom-most line of the animation panel, horizontally centered.
    - **Structure**: Usually separated from the main note by an empty line (`""`).

### Example Implementation (Rich)
```python
return Group(
    main_content,
    "",
    Align.center(Text(main_note, style="yellow")),
    "",
    Align.center(Text("Restarting animation...", style="dim italic"))
)
```

## Maintenance
When adding new command animations (e.g., `push`, `pull`), ensure they implement this restart logic to allow users to study the visualization indefinitely without manual interaction.
