@echo off
rem manifest.cmd - regenerate the dry-run manifest from the extracted exports.
rem Writes nothing to ChromaDB. Re-run this after editing classify.py.
rem
rem   manifest                       (all conversations)
rem   manifest --since 2026-06-01    (a date window)
rem
rem Override the input/output with EXPORT_ROOT / REVIEW_MANIFEST.

set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY%" (
  echo Python 3.12 not found at "%PY%".
  exit /b 1
)
if "%EXPORT_ROOT%"=="" set "EXPORT_ROOT=D:\faithh-ingest\raw"
if "%REVIEW_MANIFEST%"=="" set "REVIEW_MANIFEST=D:\faithh-ingest\manifest_v3.json"
"%PY%" "%~dp0manifest_claude_exports.py" "%EXPORT_ROOT%" --json "%REVIEW_MANIFEST%" %*
