@echo off<nul 3>nul
echo %date:~0,10% %time:~0,-3% ��ӭʹ���Զ����ӱ���У԰��
:one
echo %date:~0,10% %time:~0,-3% �ػ��������ڱ�֤У԰������...
start run.vbs
ping 127.0.0.1 -n 300>nul
goto one