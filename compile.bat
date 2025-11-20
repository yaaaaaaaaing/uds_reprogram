pyinstaller --onefile uds_ui.py --hidden-import=can.interfaces.vector --hidden-import=can.interfaces.vector.bus --hidden-import=can.interfaces.vector.channel
pause