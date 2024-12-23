@echo off
set TF_ENABLE_ONEDNN_OPTS=0
set TF_CPP_MIN_LOG_LEVEL=2
pythonw.exe divine_master_controller.py
