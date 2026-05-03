@echo off
echo Building SplitWire-Turkey C# WPF Application (Simple Build)...

REM Check if .NET SDK is installed
dotnet --version >nul 2>&1
if errorlevel 1 (
    echo Error: .NET SDK not found. Please install .NET 8.0 SDK or later.
    pause
    exit /b 1
)

REM Clean previous builds
if exist "SplitWireTurkey\bin" rmdir /s /q "SplitWireTurkey\bin"
if exist "SplitWireTurkey\obj" rmdir /s /q "SplitWireTurkey\obj"

REM Create Resources directory if it doesn't exist
if not exist "SplitWireTurkey\Resources" mkdir "SplitWireTurkey\Resources"

REM Copy resource files if they exist in the main directory
if exist "splitwire.ico" copy "splitwire.ico" "SplitWireTurkey\Resources\"
if exist "splitwire-logo-128.png" copy "splitwire-logo-128.png" "SplitWireTurkey\Resources\"
if exist "splitwireturkeytext.png" copy "splitwireturkeytext.png" "SplitWireTurkey\Resources\"
if exist "loading.gif" copy "loading.gif" "SplitWireTurkey\Resources\"
if exist "wgcf.exe" copy "wgcf.exe" "SplitWireTurkey\Resources\"
if exist "wiresock-vpn-client-x64-1.4.7.1.msi" copy "wiresock-vpn-client-x64-1.4.7.1.msi" "SplitWireTurkey\Resources\"

REM Copy font files if they exist in the main directory
if exist "Poppins-Regular.ttf" copy "Poppins-Regular.ttf" "SplitWireTurkey\Resources\"
if exist "Poppins-Bold.ttf" copy "Poppins-Bold.ttf" "SplitWireTurkey\Resources\"
if exist "Montserrat-VariableFont_wght.ttf" copy "Montserrat-VariableFont_wght.ttf" "SplitWireTurkey\Resources\"

REM Build the application
cd SplitWireTurkey
dotnet restore
if errorlevel 1 (
    echo Error: dotnet restore failed!
    cd ..
    pause
    exit /b 1
)

dotnet build -c Release
if errorlevel 1 (
    echo Error: dotnet build failed!
    cd ..
    pause
    exit /b 1
)

REM Create res folder in output directory
if not exist "bin\Release\net8.0-windows\res" mkdir "bin\Release\net8.0-windows\res"

REM Copy resource files to res folder
if exist "Resources\splitwire.ico" copy "Resources\splitwire.ico" "bin\Release\net8.0-windows\res\"
if exist "Resources\splitwire-logo-128.png" copy "Resources\splitwire-logo-128.png" "bin\Release\net8.0-windows\res\"
if exist "Resources\splitwireturkeytext.png" copy "Resources\splitwireturkeytext.png" "bin\Release\net8.0-windows\res\"
if exist "Resources\wiresock-vpn-client-x64-1.4.7.1.msi" copy "Resources\wiresock-vpn-client-x64-1.4.7.1.msi" "bin\Release\net8.0-windows\res\"

REM Copy language files to res folder
if exist "Resources\Languages" (
    if not exist "bin\Release\net8.0-windows\res\Languages" mkdir "bin\Release\net8.0-windows\res\Languages"
    if exist "Resources\Languages\tr.json" copy "Resources\Languages\tr.json" "bin\Release\net8.0-windows\res\Languages\"
    if exist "Resources\Languages\en.json" copy "Resources\Languages\en.json" "bin\Release\net8.0-windows\res\Languages\"
    if exist "Resources\Languages\ru.json" copy "Resources\Languages\ru.json" "bin\Release\net8.0-windows\res\Languages\"
    if exist "Resources\Languages\es.json" copy "Resources\Languages\es.json" "bin\Release\net8.0-windows\res\Languages\"
)

REM Check if critical files exist
if not exist "bin\Release\net8.0-windows\SplitWire-Turkey.exe" (
    echo Error: Main executable not found! Build may have failed.
    cd ..
    pause
    exit /b 1
)

REM Clean up unnecessary files (keep only .exe and .dll)
if exist "bin\Release\net8.0-windows\SplitWire-Turkey.deps.json" del "bin\Release\net8.0-windows\SplitWire-Turkey.deps.json"
if exist "bin\Release\net8.0-windows\SplitWire-Turkey.pdb" del "bin\Release\net8.0-windows\SplitWire-Turkey.pdb"
if exist "bin\Release\net8.0-windows\SplitWire-Turkey.xml" del "bin\Release\net8.0-windows\SplitWire-Turkey.xml"

REM Copy AddToRoot contents to Release folder
echo.
echo AddToRoot klasoru icerigi Release klasorune kopyalaniyor...
cd ..
if exist "AddToRoot" (
    xcopy "AddToRoot\*" "SplitWireTurkey\bin\Release\net8.0-windows\" /E /I /Y
    if errorlevel 1 (
        echo Error: AddToRoot icerigi kopyalanirken hata olustu!
        pause
        exit /b 1
    ) else (
        echo AddToRoot icerigi basariyla kopyalandi
    )
) else (
    echo Error: AddToRoot klasoru bulunamadi!
    pause
    exit /b 1
)

echo.
echo Build complete!
echo Executable created in: SplitWireTurkey\bin\Release\net8.0-windows\SplitWire-Turkey.exe
echo Resource files copied to: SplitWireTurkey\bin\Release\net8.0-windows\res\
echo AddToRoot contents copied to: SplitWireTurkey\bin\Release\net8.0-windows\
echo.
echo Note: This is a simple build without publishing. Run the executable from the bin folder.
echo.
echo Build successful! Script will continue automatically... 