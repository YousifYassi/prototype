@echo off
REM Training script for safety violation detection model
REM Uses Label Studio annotations to train a video classification model

echo ============================================================
echo Safety Violation Detection Model Training
echo ============================================================
echo.

REM Set default Label Studio export path
set LABELSTUDIO_JSON=C:\Users\yousi\Downloads\project-1-at-2025-12-17-13-45-ec1123a5.json

REM Check if custom path provided
if not "%~1"=="" set LABELSTUDIO_JSON=%~1

echo Label Studio Export: %LABELSTUDIO_JSON%
echo.

REM Check if the JSON file exists
if not exist "%LABELSTUDIO_JSON%" (
    echo ERROR: Label Studio export not found!
    echo Please provide the path to your Label Studio JSON export.
    echo.
    echo Usage: train_safety.bat [path_to_labelstudio_export.json]
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Activated virtual environment
)

echo.
echo Starting training...
echo.

REM Run the training script
python train_safety_model.py --json "%LABELSTUDIO_JSON%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo Training completed successfully!
    echo Model saved in: checkpoints\
    echo ============================================================
) else (
    echo.
    echo Training failed with error code: %ERRORLEVEL%
)

pause



