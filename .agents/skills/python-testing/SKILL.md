---
name: python-testing
description: Design and run deterministic Python tests with pytest, fixtures, temporary paths, mocks and clear behavioral assertions.
tags: [python, pytest, testing, quality]
---

# Python testing

## Test behavior, not implementation details

- Use a descriptive `test_*` name that states the expected behavior.
- Keep one main behavior per test and structure setup, action, and assertions clearly.
- Prefer small pytest fixtures, `tmp_path`, and parametrization for repeated cases.
- Mock network, external services, clocks, systemd, desktop notifications, and other host state unless the integration itself is explicitly under test.
- Test errors and boundaries as well as the normal path. Check observable results, not only that a function was called.

## Safe and reproducible runs

- Read the existing pytest configuration and follow its test command and markers.
- Do not let tests write to the real home directory, system service paths, user databases, or the network.
- Use a temporary project/config path and restore patched environment variables with pytest facilities.
- Keep tests independent and clean up subprocesses and temporary resources.
- Report the exact command and pass/fail/skip counts; a skipped test is not a passing integration test.
