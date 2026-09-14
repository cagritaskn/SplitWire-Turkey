@echo off
setlocal enabledelayedexpansion

set "MODERN_APP_SVC=WireSockAppService"
set "MODERN_CONNECT_SVC=WireSockConnectService"
set "LEGACY_SVC=wiresock-client-service"

REM Modern WireSock 3.x servislerinden herhangi biri kayıtlı mı kontrol et
set "HAS_APP_SVC=0"
sc query "%MODERN_APP_SVC%" >nul 2>&1
if not errorlevel 1 set "HAS_APP_SVC=1"

set "HAS_CONNECT_SVC=0"
sc query "%MODERN_CONNECT_SVC%" >nul 2>&1
if not errorlevel 1 set "HAS_CONNECT_SVC=1"

if "%HAS_APP_SVC%"=="1" goto :modern
if "%HAS_CONNECT_SVC%"=="1" goto :modern

REM Legacy WireSock servisini kontrol et
sc query "%LEGACY_SVC%" >nul 2>&1
if not errorlevel 1 goto :legacy

goto :done

:modern
REM Her iki modern servisin durumunu ayrı ayrı kontrol et (kayıtlı değilse
REM zaten "sorun yok" say, çünkü bu kurulumda kullanılmıyor demektir)
set "APP_RUNNING=1"
if not "%HAS_APP_SVC%"=="1" goto :check_connect
set "APP_RUNNING=0"
for /f "tokens=4" %%a in ('sc query "%MODERN_APP_SVC%" ^| findstr "STATE"') do set "appstate=%%a"
if /i "%appstate%"=="RUNNING" set "APP_RUNNING=1"

:check_connect
set "CONNECT_RUNNING=1"
if not "%HAS_CONNECT_SVC%"=="1" goto :eval_modern
set "CONNECT_RUNNING=0"
for /f "tokens=4" %%a in ('sc query "%MODERN_CONNECT_SVC%" ^| findstr "STATE"') do set "constate=%%a"
if /i "%constate%"=="RUNNING" set "CONNECT_RUNNING=1"

:eval_modern
REM Her iki servis de zaten çalışıyorsa dokunma (gereksiz restart, WireGuard
REM NDIS adaptörünün sürekli yeniden oluşturulmasına ve nadir de olsa IRQL
REM çakışmalarına yol açabiliyor)
if "%APP_RUNNING%"=="1" if "%CONNECT_RUNNING%"=="1" goto :done

REM Eksik/durmuş olan(lar)ı başlat
if "%HAS_APP_SVC%"=="1" if "%APP_RUNNING%"=="0" sc start "%MODERN_APP_SVC%" >nul 2>&1
if "%HAS_CONNECT_SVC%"=="1" if "%CONNECT_RUNNING%"=="0" sc start "%MODERN_CONNECT_SVC%" >nul 2>&1

timeout /t 5 /nobreak >nul

REM WireSock 3.x'te servislerin RUNNING olması tünelin de aktif olduğu
REM anlamına gelmiyor -- profil bağlantısının CLI ile yeniden kurulması
REM gerekiyor (bkz. WireSockService.cs StartServiceAsync/InstallServiceAsync)
set "CLI_PATH=%ProgramFiles%\WireSock Secure Connect\command-line\wiresock-connect-cli.exe"
if not exist "%CLI_PATH%" set "CLI_PATH=%ProgramFiles(x86)%\WireSock Secure Connect\command-line\wiresock-connect-cli.exe"
if not exist "%CLI_PATH%" set "CLI_PATH="

if not defined CLI_PATH goto :done
"%CLI_PATH%" connect wgcf-profile -exit >nul 2>&1

goto :done

:legacy
REM Legacy WireSock (1.4.7.1/2.x): config servis kurulumuna gömülü olduğu
REM için basit bir servis restart'ı tüneli de geri getiriyor
for /f "tokens=4" %%a in ('sc query "%LEGACY_SVC%" ^| findstr "STATE"') do set "state=%%a"
if /i "!state!"=="RUNNING" goto :done

sc start "%LEGACY_SVC%" >nul 2>&1

timeout /t 5 /nobreak >nul

set "attempt=1"
:retry
for /f "tokens=4" %%a in ('sc query "%LEGACY_SVC%" ^| findstr "STATE"') do set "state=%%a"

if /i "!state!"=="RUNNING" (
    goto :done
) else (
    if !attempt! lss 3 (
        set /a attempt+=1
        sc start "%LEGACY_SVC%" >nul 2>&1
        timeout /t 5 /nobreak >nul
        goto :retry
    )
)

:done
endlocal
