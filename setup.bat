@echo off
echo Setting up eBird Rare Bird Alert Monitor...

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Conda not found. Please install Miniconda or Anaconda first.
    echo Visit: https://docs.conda.io/en/latest/miniconda.html
    exit /b 1
)

REM Create conda environment from environment.yml
echo Creating conda environment 'ebird-rba'...
call conda env create -f environment.yml

if %ERRORLEVEL% neq 0 (
    echo Failed to create conda environment.
    exit /b 1
)

REM Create .env file from template if it doesn't exist
if not exist config\.env (
    echo Creating config/.env from template...
    copy config\.env.template config\.env
    echo Please edit config/.env with your notification credentials.
) else (
    echo config/.env already exists, skipping creation.
)

REM Create logs directory if it doesn't exist
if not exist logs (
    echo Creating logs directory...
    mkdir logs
)

echo.
echo Setup complete!
echo.
echo To activate the environment and run the program:
echo   conda activate ebird-rba
echo   python run.py
echo.