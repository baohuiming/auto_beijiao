@echo off<nul 3>nul
echo %date:~0,10% %time:~0,-3% 欢迎使用自动连接北交校园网
:one
echo %date:~0,10% %time:~0,-3% 守护进程正在保证校园网连接...
start run.vbs
ping 127.0.0.1 -n 300>nul
goto one