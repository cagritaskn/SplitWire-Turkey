@echo off
setlocal enabledelayedexpansion

set "MODERN_APP_SVC=WireSockAppService"
set "MODERN_CONNECT_SVC=WireSockConnectService"
set "LEGACY_SVC=wiresock-client-service"
set "TASK_NAME=WireSockRefresh"

REM Detect which of the modern WireSock 3.x services are registered
set "HAS_APP_SVC=0"
sc query "%MODERN_APP_SVC%" >nul 2>&1
if not errorlevel 1 set "HAS_APP_SVC=1"

set "HAS_CONNECT_SVC=0"
sc query "%MODERN_CONNECT_SVC%" >nul 2>&1
if not errorlevel 1 set "HAS_CONNECT_SVC=1"

if "%HAS_APP_SVC%"=="1" goto :modern
if "%HAS_CONNECT_SVC%"=="1" goto :modern

REM Check for the legacy WireSock service
sc query "%LEGACY_SVC%" >nul 2>&1
if not errorlevel 1 goto :legacy

goto :done

:modern
REM Check each modern service's state separately (not registered = treat as
REM "not a problem", since this install simply does not use it)
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
REM Both already running -- do not touch anything. An unconditional restart
REM here is what used to tear down and rebuild WireSock's WireGuard NDIS
REM adapter every cycle, which could trigger a rare NDIS-level IRQL crash
REM (BSOD 0x0A) on some systems. Only intervene when something is really down.
if "%APP_RUNNING%"=="1" if "%CONNECT_RUNNING%"=="1" goto :done

REM Start only the service(s) that are actually down
if "%HAS_APP_SVC%"=="1" if "%APP_RUNNING%"=="0" sc start "%MODERN_APP_SVC%" >nul 2>&1
if "%HAS_CONNECT_SVC%"=="1" if "%CONNECT_RUNNING%"=="0" sc start "%MODERN_CONNECT_SVC%" >nul 2>&1

timeout /t 5 /nobreak >nul

REM Verify recovery actually worked for whichever service(s) we touched. If a
REM service we tried to start is still not running, something is genuinely
REM wrong -- do not keep retrying every 3 minutes forever (that repeated
REM retry pattern is exactly the kind of behavior that risks the same class
REM of crash). Instead, disable this watchdog immediately and safely.
set "RECOVERY_OK=1"

if "%HAS_APP_SVC%"=="1" if "%APP_RUNNING%"=="0" (
    for /f "tokens=4" %%a in ('sc query "%MODERN_APP_SVC%" ^| findstr "STATE"') do set "appstate2=%%a"
    if /i not "!appstate2!"=="RUNNING" set "RECOVERY_OK=0"
)

if "%HAS_CONNECT_SVC%"=="1" if "%CONNECT_RUNNING%"=="0" (
    for /f "tokens=4" %%a in ('sc query "%MODERN_CONNECT_SVC%" ^| findstr "STATE"') do set "constate2=%%a"
    if /i not "!constate2!"=="RUNNING" set "RECOVERY_OK=0"
)

if "%RECOVERY_OK%"=="0" goto :self_disable

REM WireSock 3.x: a RUNNING service does not by itself mean the tunnel is
REM active -- the profile connection has to be re-established through the
REM CLI (see WireSockService.cs StartServiceAsync/InstallServiceAsync). This
REM is a lightweight client call to the already-running daemon, not a
REM service restart, so it does not rebuild the network adapter.
set "CLI_PATH=%ProgramFiles%\WireSock Secure Connect\command-line\wiresock-connect-cli.exe"
if not exist "%CLI_PATH%" set "CLI_PATH=%ProgramFiles(x86)%\WireSock Secure Connect\command-line\wiresock-connect-cli.exe"
if not exist "%CLI_PATH%" set "CLI_PATH="

if not defined CLI_PATH goto :done
"%CLI_PATH%" connect wgcf-profile -exit >nul 2>&1

goto :done

:legacy
REM Legacy WireSock (1.4.7.1/2.x): the config is embedded in the service
REM install, so a plain service restart also brings the tunnel back
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

REM Exhausted all retries and the service still is not running -- same
REM self-preservation policy as the modern branch applies here.
goto :self_disable

:self_disable
REM Something is genuinely wrong with recovering WireSock through this
REM watchdog. Rather than keep firing every 3 minutes and repeatedly
REM restarting a service that will not come back, remove this scheduled
REM task entirely and stop. The user can always re-enable the repeater
REM from the app if they want to try again.
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
goto :done

:done
endlocal
