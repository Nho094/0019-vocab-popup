---
name: python-script-developer
description: Build and maintain small, reliable Python scripts and command-line tools, including Linux desktop utilities, scheduled jobs, configuration and logging.
tags: [python, scripting, cli, linux]
---

# Python script developer

## Start with the existing project

- Inspect its entry points, dependency files, supported Python version, tests, and conventions before changing anything.
- Prefer the standard library for small utilities. Add a dependency only when it solves a real requirement and can be installed through the project's documented environment.
- Keep modules focused. Put reusable logic in importable functions and keep process startup behind `if __name__ == "__main__":`.

## Reliable command-line applications

- Parse arguments with `argparse` unless the project already uses another CLI framework.
- Use `pathlib`, explicit UTF-8 for text, and clear errors with non-zero exit codes for failure.
- Keep user data/configuration in documented user-scoped paths; do not hard-code a machine-specific home directory.
- Make recurring jobs idempotent and safe to rerun. Do not silently overwrite user data.
- Use Python logging for diagnostics. Avoid logging secrets or full private user content.
- For desktop utilities, separate UI, vocabulary/data access, and scheduling so each can be tested independently.

## Linux background work

For periodic desktop work, prefer an explicit user-level systemd timer when suitable. Do not install, enable, or start a unit, use `sudo`, or modify system directories without the user's explicit approval. See `systemd-services` when unit/timer details are needed.

## Verification

Add tests for normal behavior, invalid input, missing files, and repeat execution. Run the project's declared checks; do not claim a live desktop or systemd integration was tested when only unit tests ran.
