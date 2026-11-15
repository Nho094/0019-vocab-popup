---
name: systemd-services
description: Create and troubleshoot Linux systemd user services and timers for Python applications. Use when scheduling recurring jobs, running a desktop helper in the background, or packaging a Linux app as a service.
tags: [linux, systemd, services, timers]
---

# systemd services and timers

Use this skill when a Linux application needs to run in the background or on a schedule.

## Safe workflow

1. Determine whether this should be a foreground desktop app, a user service, or a system service. Prefer a user service for a per-user app; do not use `sudo` or `/etc/systemd/system` by default.
2. Read the project's current launch command, paths, environment needs, and packaging before writing unit files.
3. Prefer a `.timer` plus a `Type=oneshot` service for periodic work. Choose `OnUnitActiveSec=` or `OnCalendar=` based on the required timing, and document startup/first-run behavior.
4. Use absolute executable and working-directory paths in `ExecStart` and `WorkingDirectory`. Do not put shell syntax in `ExecStart`; if a wrapper is needed, create and test a project-owned script.
5. Keep credentials out of unit files and logs. Use least-privilege user settings and systemd hardening where compatible.
6. Validate generated units with `systemd-analyze verify` when available. Report when systemd is unavailable instead of claiming runtime verification.

## Permission boundary

Creating unit files inside the project is ordinary file work. Enabling, starting, stopping, restarting, disabling, or editing an installed unit changes the user's system state: show the exact command and ask for explicit approval first. Never use `sudo`, enable a system-wide unit, or alter files under `/etc` unless the user explicitly requests that exact operation.

Do not run service-management commands merely because a task asks to write or test a unit. Tests should use temporary files and mocked `systemctl` calls.
