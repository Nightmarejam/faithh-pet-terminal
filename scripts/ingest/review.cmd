@echo off
rem review.cmd - run the manifest review tool from anywhere, with the current
rem manifest already filled in. Unaffected by PowerShell execution policy and by
rem whichever "python" happens to be first on PATH.
rem
rem   review --runbook
rem   review --mode journal --sort chars
rem   review --unclassified
rem   review --timeline
rem   review --nuggets
rem   review --topic audio --since 2026-04-01
rem
rem Point REVIEW_MANIFEST at a different .json to review another run.

set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY%" (
  echo Python 3.12 not found at "%PY%".
  exit /b 1
)
if "%REVIEW_MANIFEST%"=="" set "REVIEW_MANIFEST=D:\faithh-ingest\manifest_v3.json"
if not exist "%REVIEW_MANIFEST%" (
  echo Manifest not found: "%REVIEW_MANIFEST%"
  echo Regenerate it with manifest.cmd, or set REVIEW_MANIFEST to another file.
  exit /b 1
)
"%PY%" "%~dp0review_manifest.py" "%REVIEW_MANIFEST%" %*
