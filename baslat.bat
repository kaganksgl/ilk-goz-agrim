@echo off
rem Ilk Goz Agrim - uygulamayi baslatir. Kurulum icin once kur.bat calistirilir.
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto :run
echo Uygulama henüz kurulmamış. Önce kur.bat dosyasını çalıştırın.
pause
exit /b 1
:run
rem Günlük penceresi simge durumunda açılır; uygulama kapanınca o da kapanır.
start "İlk Göz Ağrım - günlük" /min ".venv\Scripts\python.exe" main.py
