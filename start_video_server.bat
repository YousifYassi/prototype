@echo off
echo ============================================================
echo Starting Video File Server for Label Studio
echo ============================================================
echo.
echo This server makes your local videos accessible to Label Studio
echo Keep this window open while annotating!
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python serve_videos.py

pause


