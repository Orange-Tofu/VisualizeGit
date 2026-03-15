# Terminal Split UI with Python --- Concept Overview

## Goal

The objective is to build a **terminal interface that is divided into
two independent sections**:

-   **Part A** -- Displays ASCII art, animation, or status information.
-   **Part B** -- Displays the **live output of a running command** (for
    example `git push`, `sftp`, `ping`, etc.).

Instead of the terminal behaving like a normal scrolling log, the screen
behaves more like a **dashboard layout**.

------------------------------------------------------------------------

## Desired Terminal Layout

    ┌────────────────────────────────────────────┐
    │ Part A                                     │
    │                                            │
    │ ASCII animation / status / explanation     │
    │                                            │
    ├────────────────────────────────────────────┤
    │ Part B                                     │
    │                                            │
    │ Live command output (git push, sftp etc.)  │
    │                                            │
    └────────────────────────────────────────────┘

### Behavior

  -----------------------------------------------------------------------
  Section                             Role
  ----------------------------------- -----------------------------------
  **Part A**                          Shows UI elements such as
                                      animations, progress indicators, or
                                      explanations

  **Divider**                         Separates the two areas visually

  **Part B**                          Streams the output of a command in
                                      real time
  -----------------------------------------------------------------------

Example use case:

    Part A:
    Uploading files to remote repository...
    [spinning animation]

    Part B:
    git push output:
    Counting objects: 42
    Compressing objects...
    Writing objects...

When the command finishes:

-   The animation stops
-   The program exits
-   The full output may optionally be shown again

------------------------------------------------------------------------

# Why a Normal Terminal Cannot Do This

Normally the terminal prints text sequentially:

    line1
    line2
    line3

Once printed, earlier lines cannot easily be updated.

Your requirement needs:

-   Fixed areas of the screen
-   Independent updates
-   No interference between sections

This requires **direct control of the terminal screen**.

------------------------------------------------------------------------

# Solution: Text User Interface (TUI)

To achieve this, the program uses a **Text User Interface (TUI)**
approach.

A TUI treats the terminal as a **grid of cells** that can be redrawn at
any time rather than as a simple text stream.

This allows:

-   Dividing the terminal into regions
-   Updating different parts independently
-   Creating animations
-   Displaying live command output

------------------------------------------------------------------------

# Screen Structure

The terminal screen is divided into three parts:

1.  **Top Window (Part A)**
2.  **Divider Line**
3.  **Bottom Window (Part B)**

Example conceptual structure:

    Row 0–19   → Part A
    Row 20     → Divider
    Row 21–39  → Part B

Each region behaves like its own **mini terminal window**.

------------------------------------------------------------------------

# Part A --- Animation or Status UI

Part A continuously displays visual information.

Examples:

-   ASCII animation
-   Progress spinner
-   Status messages
-   Descriptions of the command being run

These frames are redrawn repeatedly to create the appearance of
animation.

The animation continues running **while the command is executing**.

------------------------------------------------------------------------

# Part B --- Live Command Output

Part B is responsible for running a **real system command** and
displaying its output as it happens.

Example commands:

-   `git push`
-   `sftp`
-   `ping`
-   `ls`
-   `scp`

Instead of waiting for the command to finish, the program reads the
output **as the command produces it**.

Example streamed output:

    Counting objects: 42
    Compressing objects...
    Writing objects...
    Done

Each line is immediately written to the lower section of the screen.

------------------------------------------------------------------------

# Concurrent Execution

Two independent activities must occur at the same time:

  Activity            Purpose
  ------------------- -------------------------------------
  Animation           Keeps the interface visually active
  Command Execution   Runs and streams command output

To allow both tasks to run simultaneously, the system runs them **in
parallel**.

Conceptually:

    Thread 1 → Animation loop
    Thread 2 → Command execution + output streaming

Both threads update their assigned section of the terminal.

------------------------------------------------------------------------

# Preventing Screen Conflicts

Because multiple tasks may try to update the terminal at the same time,
access to the screen must be **synchronized**.

Without synchronization, problems can occur such as:

-   Output appearing in the wrong section
-   Screen corruption
-   Mixed text from different parts

To avoid this, updates are coordinated so that **only one operation
writes to the screen at a time**.

------------------------------------------------------------------------

# Controlling When Animation Stops

The animation should run **only while the command is running**.

When the command completes:

1.  The animation stops
2.  Both sections finish updating
3.  The program exits

A shared signal mechanism is used so that when the command finishes, the
animation receives a stop signal.

------------------------------------------------------------------------

# Capturing Command Output

While displaying output live, the program also **stores the output
internally**.

This allows the program to later:

-   Print the full command output again
-   Save it to a file
-   Process it programmatically

Example stored output:

    Counting objects: 42
    Compressing objects...
    Writing objects...
    Done

------------------------------------------------------------------------

# Overall Architecture

Conceptually the system works like this:

                    Python Program
                          │
            ┌─────────────┴─────────────┐
            │                           │
       Animation System           Command Runner
            │                           │
       Updates Part A             Streams command output
            │                           │
            └─────────────┬─────────────┘
                          │
                   Terminal Screen
                          │
            ┌─────────────┴─────────────┐
            │                           │
            Part A                   Part B
       ASCII Animation        Live Command Output

------------------------------------------------------------------------

# Real-World Examples of This Pattern

This design pattern is widely used in modern CLI tools.

Examples include:

### Docker

Shows progress animations while pulling images.

### GitHub CLI

Displays progress indicators while uploading files.

### Continuous Integration Tools

Display a status panel with logs streaming below.

### File Transfer Tools

Show transfer status animations while printing transfer logs.

------------------------------------------------------------------------

# What This System Essentially Is

You are effectively building a **Terminal Dashboard System**.

In technical terms, this is known as a:

**Text User Interface (TUI)**

Many modern tools use specialized frameworks to build these interfaces.

Common libraries include:

-   curses
-   rich
-   textual
-   urwid
-   blessed

------------------------------------------------------------------------

# Key Features of Your System

The system you designed supports:

-   Split terminal layout
-   Real-time command output streaming
-   ASCII animations
-   Concurrent execution
-   Controlled screen updates
-   Output capture
-   Graceful termination

This architecture is a **solid foundation for building advanced CLI
tools**.
