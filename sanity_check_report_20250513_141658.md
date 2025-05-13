# AI Dev Toolkit Simple Sanity Check Report

Found **3** issues and **4** warnings.

## Issues
- Syntax error in aitoolkit/gui/configurator.py:253: invalid syntax. Perhaps you forgot a comma? (configurator.py, line 253)
- Syntax error in aitoolkit/server/main.py:267: expected an indented block after 'if' statement on line 265 (main.py, line 267)
- Syntax error in legacy/fix_config.py:90: positional argument follows keyword argument (fix_config.py, line 90)

## Warnings
- Duplicate file name: server.py
- Duplicate file name: __init__.py
- Duplicate file name: filesystem.py
- Code may need to be migrated from src/ to aitoolkit/

## Overall Status
**Failed** - Please fix the issues before continuing