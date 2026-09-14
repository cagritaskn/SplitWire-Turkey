@echo off
cd /d "%~dp0"

REM Zapret tek seferlik çalıştırma
REM Parametreler komut satırından alınacak

if "%1"=="" (
    echo HATA: Parametre belirtilmedi!
    echo Kullanım: onetime_batch.cmd [zapret_parametreleri]
    pause
    exit /b 1
)

echo Zapret tek seferlik çalıştırılıyor...
echo Parametreler: %*

REM Zapret'i çalıştır
"%~dp0winws.exe" %* --hostlist-exclude=%~dp0splitwire-exclude.txt

if %ERRORLEVEL% EQU 0 (
    echo Zapret başarıyla çalıştırıldı.
) else (
    echo Zapret çalıştırılırken hata oluştu. Hata kodu: %ERRORLEVEL%
)

pause

