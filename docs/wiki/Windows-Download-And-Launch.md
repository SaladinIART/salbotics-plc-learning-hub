# Windows Download And Launch

Use this guide if you are not cloning with Git yet.

## Requirements

- Windows 10 or Windows 11.
- Python 3.11 or newer.
- A modern browser.
- Internet access during first launch so Python packages can install.

No PLC, VFD, sensor, Arduino, Raspberry Pi, COM port, or industrial hardware is required.

## Download From GitHub

1. Open the repository: https://github.com/SaladinIART/salbotics-plc-learning-hub
2. Click the green **Code** button.
3. Click **Download ZIP**.
4. Right-click the downloaded ZIP file.
5. Choose **Extract All...**.
6. Open the extracted folder.

## Launch

1. Double-click `start-plc-trainer.bat`.
2. Wait for the launcher to create `.venv`.
3. Wait for dependencies to install.
4. The browser should open `http://127.0.0.1:8733`.
5. Keep the server window open while using the trainer.

## If Phase 3 Shows No Data

If the Phase 3 page says **NO DATA** and the server window shows `404` for `/api/analytics/*`, an old server is probably still running on port `8733`.

Run `start-plc-trainer.bat` again. If it asks whether to stop the existing process and restart this trainer, choose `Y`.

## Current Limitation

The one-click launcher is designed for Windows. Linux and macOS launch scripts are not included yet.
