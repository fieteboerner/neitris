@echo off
cls
echo Starting Neitris Server and Client
cd %~dp0
start python neitris_server.py
start python neitris.py 127.0.0.1