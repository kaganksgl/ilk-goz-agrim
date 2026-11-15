@echo off
rem Ilk Goz Agrim - kurulum: sanal ortam, paketler, model dosyasi.
rem Yeniden calistirmak guvenlidir; tamamlanan adimlar atlanir, yarim kalan indirme surdurulur.
chcp 65001 >nul
set "PYTHONUTF8=1"
setlocal
cd /d "%~dp0"
title İlk Göz Ağrım - Kurulum

echo.
echo  İlk Göz Ağrım - kurulum
echo  =======================
echo  Gerekenler: Windows 10/11 (64 bit), Python 3.12, ~7 GB boş disk alanı, internet bağlantısı.
echo  İnternet yalnızca bu kurulum için gerekir; uygulama internete bağlanmaz.
echo.

rem ---- 1/4 Python 3.12 --------------------------------------------------------
set "PY="
py -3.12 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3.12"
if defined PY goto :have_python
python -c "import sys; raise SystemExit(sys.version_info[:2] != (3, 12))" >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto :have_python
echo [HATA] Python 3.12 bulunamadı.
echo        https://www.python.org/downloads/ adresinden Python 3.12 (64 bit) kurun,
echo        ardından bu dosyayı yeniden çalıştırın.
goto :fail

:have_python
echo [1/4] Python 3.12 bulundu.

rem ---- 2/4 sanal ortam --------------------------------------------------------
if exist ".venv\Scripts\python.exe" goto :have_venv
echo [2/4] Sanal ortam oluşturuluyor (.venv)...
%PY% -m venv .venv
if errorlevel 1 goto :fail
goto :packages
:have_venv
echo [2/4] Sanal ortam hazır (.venv).

rem ---- 3/4 paketler -----------------------------------------------------------
:packages
echo [3/4] Paketler kuruluyor (yaklaşık 350 MB)...
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo [HATA] Paketler kurulamadı. İnternet bağlantınızı kontrol edip yeniden deneyin.
    goto :fail
)
".venv\Scripts\python.exe" -c "import llama_cpp, PySide6.QtWidgets" >nul 2>&1
if errorlevel 1 (
    echo [HATA] Model motoru yüklenemedi. Büyük olasılıkla "Microsoft Visual C++ Redistributable" eksik.
    echo        https://aka.ms/vs/17/release/vc_redist.x64.exe dosyasını kurup bu dosyayı yeniden çalıştırın.
    goto :fail
)

rem ---- 4/4 model --------------------------------------------------------------
echo [4/4] Model dosyası (Gemma 4 E4B, 5,2 GB) indiriliyor ve doğrulanıyor...
".venv\Scripts\python.exe" tools\download_model.py
if errorlevel 1 goto :fail

echo.
echo  Kurulum tamamlandı. Uygulamayı açmak için baslat.bat dosyasına çift tıklayın.
echo.
if not defined ILK_GOZ_AGRIM_NO_PAUSE pause
exit /b 0

:fail
echo.
echo  Kurulum tamamlanamadı. Sorun giderme: README.md
echo.
if not defined ILK_GOZ_AGRIM_NO_PAUSE pause
exit /b 1
