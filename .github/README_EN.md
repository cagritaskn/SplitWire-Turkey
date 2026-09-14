<p align="center">
  <img width="auto" height="128" src="https://github.com/cagritaskn/SplitWire-Turkey/blob/main/src/SplitWireTurkey/Resources/splitwire-logo-128.png">
</p>

# <p align="center"><strong>SplitWire-Turkey</strong></p>

<div align="center">

<strong>Multilingual README (TR/EN/RU/ES)</strong>

[![TR](https://img.shields.io/badge/README-TR-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/README.md)
[![EN](https://img.shields.io/badge/README-EN-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_EN.md)
[![RU](https://img.shields.io/badge/README-RU-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_RU.md)
[![ES](https://img.shields.io/badge/README-ES-blue.svg)](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_ES.md)

</div>

# SplitWire-Turkey

**SplitWire-Turkey** is a DPI bypass and tunneling automation project specifically designed for internet users in Turkey. It is an open-source Windows application that helps bypass restrictions without affecting your internet connection speed. This tool allows you to automatically install and manage many bypass methods from a single interface. Since it performs service installation, you don't need to perform any additional operations to access the relevant applications when you restart your computer. The source code of this completely open-source application is available in the /src folder in the repository.

---

## Video User Guide

You can follow the installation and usage instructions from the video guide prepared by Recep Baltaş below:

<a href="https://www.youtube.com/watch?v=LtwsTy568rw"> <img src="https://img.youtube.com/vi/LtwsTy568rw/maxresdefault.jpg" width="310"> </a> <br> <a href="https://www.youtube.com/watch?v=LtwsTy568rw"> <strong>SplitWire-Turkey Video User Guide</strong> </a>

---

# Download and Installation

## Installation with Setup File (Recommended) [![Download Setup](https://img.shields.io/badge/Download-Setup-blue?logo=windows)](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.7/SplitWire-Turkey-Setup-Windows-1.5.7.exe)
- Download the **[SplitWire-Turkey Setup](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.7/SplitWire-Turkey-Setup-Windows-1.5.7.exe)** installation package and perform the SplitWire-Turkey installation. (If you get a SmartScreen "Windows protected your personal computer" warning, click "More info" and then click "Run anyway", information about virus scanning and this warning is provided below)
- Open the **SplitWire-Turkey** application.
- Follow the **Usage Guides** section for using the application.

## Usage with ZIP File (Not Recommended) [![Download ZIP](https://img.shields.io/badge/Download-ZIP-blue?logo=windows)](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.7/SplitWire-Turkey-ZIP-Windows-1.5.7.zip)
- Download the **[SplitWire-Turkey ZIP](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.7/SplitWire-Turkey-ZIP-Windows-1.5.7.zip)** file and extract it to a folder.
- Open the **SplitWire-Turkey.exe** application in the folder where you extracted the ZIP file. (If you get a SmartScreen "Windows protected your personal computer" warning, click "More info" and then click "Run anyway", information about virus scanning and this warning is provided below)
- Follow the **Usage Guides** section for using the application.

---

# Usage Guides

## WireSock Usage

**Note:** The installations in this section work only for the Discord application (browsers are also included if you have enabled browser tunneling). After performing these installations, the relevant method will automatically start working every time you restart your system.

- **WS Standard Installation:** Installs WireSock 3.4.8.1 together with ByeDPI-Drover; text channels are routed via ByeDPI, voice channels via WireSock. (If the "Tunnel for browsers too" option is enabled, tunneling is also performed for internet browsers)

- **WS Alternative Installation:** Installs standalone WireSock 3.4.8.1 only (without ByeDPI and Drover); all traffic is tunneled directly through WireSock. (If the "Tunnel for browsers too" option is enabled, tunneling is also performed for internet browsers)

- **Tunnel for browsers too:** In addition to the Discord application; tunneling is performed for popular internet browsers such as Chrome, Firefox, Opera, OperaGX, Brave, Vivaldi, Zen, Chromium and Edge.

- **Install WireSock repeater:** Creates a WTS task that restarts WireSock at regular intervals. Only activate and install if you experience problems. This Windows Task Scheduler task restarts the WireSock service at regular intervals.

- **Customize folder list:** You can use this section if you want to perform tunneling for an application other than Discord.
  - **Add Folder:** Selects the folder where the application you want to tunnel is located and adds it to the list.
  - **Clear List:** Clears the folder list.
  - **Custom Installation:** Performs installation using Wgcf and WireSock for your prepared folder list.
  - **Create Custom Config:** Creates a configuration file for your prepared folder list.

- **Exit:** Closes the program.

**Note 2:** If the Discord application gets stuck on the "Checking for updates..." screen, turn off your modem, wait 15 seconds, then turn it back on and restart your computer.

---

## ByeDPI Page Usage

**Note:** The installations in this section work only for the Discord application (browsers are also included if you have enabled browser tunneling). After performing these installations, the relevant method will automatically start working every time you restart your system.

- **ByeDPI Split Tunneling Installation:** Performs DPI bypass only for the Discord application using ByeDPI and ProxiFyre tools. (If the "Tunnel for browsers too" option is enabled, DPI bypass is also performed for internet browsers)

- **Tunnel for browsers too:** In addition to the Discord application; DPI bypass is performed for popular internet browsers such as Chrome, Firefox, Opera, OperaGX, Brave, Vivaldi and Edge. To change the browser tunneling option and perform installation again, you must first remove ByeDPI by clicking the Remove ByeDPI button.

- **ByeDPI DLL Installation:** Performs DPI bypass for **ONLY** the Discord application using ByeDPI and drover (DLL hijacking method). This method only works for the Discord application, it does not work for browsers or other programs.

- **Remove ByeDPI:** Removes ByeDPI and deletes drover files.

**Note 2:** If the Discord application gets stuck on the "Checking for updates..." screen, turn off your modem, wait 15 seconds, then turn it back on and restart your computer.

---

## Zapret Page Usage

**Note:** The installations in this section work system-wide. Although they do not cause speed loss, they may cause connection problems in some websites and applications. After performing these installations, the relevant method will automatically start working every time you restart your system.

- **Zapret Automatic Installation:** Ideal parameters are found for your system and internet service provider using Zapret's blockcheck strategy finding software, and DPI bypass is provided by installing Zapret with these parameters.

- **Scanning:** Selects the speed of the scan performed to find ideal parameters.
  - **Fast:** Can take 2-10 minutes.
  - **Standard:** Can take 5-30 minutes.
  - **Full:** Can take 10-50 minutes.

> These times are estimated times. They may vary depending on your system and your internet provider's packet inspection policies.

- **Ready Settings:** Selects one of the predetermined parameters for Zapret. (Thanks to Bal Porsuğu for the ready settings)

- **Edit Ready Settings:** Opens a text box that allows you to fine-tune or modify the ready setting you selected. After making edits in this box, you can install or run once using the parameters in the box with the buttons below.

- **Install Ready Service:** Installs the Zapret service with your selected ready setting (or the edited version if you made edits).

- **Ready One-time:** Runs Zapret once with your selected ready setting (or the edited version if you made edits). When you close the opened console window, Zapret stops running.

- **Remove Zapret:** Removes Zapret.

**Note 2:** If the Discord application gets stuck on the "Checking for updates..." screen, turn off your modem, wait 15 seconds, then turn it back on and restart your computer.

---

## Zapret2 Page Usage

**Note:** The installations in this section work system-wide. Although they do not cause speed loss, they may cause connection problems in some websites and applications. After performing these installations, the relevant method will automatically start working every time you restart your system.

- **Zapret2 Automatic Installation:** Ideal parameters are found for your system and internet service provider using Zapret2's blockcheck strategy finding software, and DPI bypass is provided by installing Zapret2 with these parameters.

- **Scanning:** Selects the speed of the scan performed to find ideal parameters.
  - **Fast:** Can take 2-10 minutes.
  - **Standard:** Can take 5-30 minutes.
  - **Full:** Can take 10-50 minutes.

> These times are estimated times. They may vary depending on your system and your internet provider's packet inspection policies.

- **Ready Settings:** Selects one of the predetermined parameters for Zapret2. Presets for Türk Telekom, Superonline, Vodafone, Türksat Kablonet, Telekom Mobil, Turkcell Mobil and Vodafone Mobil are included; these are also tried automatically before a full scan in Automatic Installation. (Thanks to Bal Porsuğu for the ready settings)

- **Edit Ready Settings:** Opens a text box that allows you to fine-tune or modify the ready setting you selected. After making edits in this box, you can install or run once using the parameters in the box with the buttons below.

- **Use Exclusion List:** Uses a list of domains that Zapret2 will not apply DPI bypass to (will not touch). If you turn it off, the list is temporarily emptied (no need to restart Zapret2, the change is applied automatically); when you turn it back on, the same list comes back.

- **Edit Exclusion List:** Opens a text box where you can edit the domains in the exclusion list. After editing, you can save the changes by clicking the Save button.

- **Install Ready Service:** Installs the Zapret2 service with your selected ready setting (or the edited version if you made edits).

- **Ready One-time:** Runs Zapret2 once with your selected ready setting (or the edited version if you made edits). When you close the opened console window, Zapret2 stops running.

- **Remove Zapret2:** Removes Zapret2.

**Note 2:** If the Discord application gets stuck on the "Checking for updates..." screen, turn off your modem, wait 15 seconds, then turn it back on and restart your computer.

---

## GoodbyeDPI Page Usage

**Note:** The installation in this section works system-wide. Although it does not cause speed loss, it may cause connection problems in some websites and applications. To prevent such problems, you can activate the "Use blacklist" option. After performing this installation, the relevant method will automatically start working every time you restart your system.

- **Ready Settings:** Selects one of the predetermined parameters for GoodbyeDPI.

- **Edit Ready Settings:** Opens a text box that allows you to fine-tune or modify the ready setting you selected. After making edits in this box, you can install or run once using the parameters in the box with the buttons below.

- **Use Blacklist:** Runs GoodbyeDPI only for preferred domains. By default, blacklist is used for Discord, Roblox and Wattpad.

- **Edit Blacklist:** Opens a text box where you can edit the domain list that GoodbyeDPI will affect. After making the edit, you can save the changes by clicking the Save button.

- **Install Service:** Installs the GoodbyeDPI service according to your preferences specified above (Ready settings and blacklist preferences).

- **One-time:** Runs GoodbyeDPI once according to your preferences specified above (Ready settings and blacklist preferences). When you close the opened console window, GoodbyeDPI stops running.

- **Remove GoodbyeDPI:** Removes GoodbyeDPI.

**Note 2:** If the Discord application gets stuck on the "Checking for updates..." screen, turn off your modem, wait 15 seconds, then turn it back on and restart your computer.

---

## Repair Page Usage

**Note:** You can try to solve Discord's "Checking for updates..." and "Starting..." screen hanging problems using the buttons on this page. First, try to repair the standard version of Discord installed on your system using the Repair Discord button, if this fails, try to solve your problem by downloading the alternative "Public Test Build" version using the Install Discord PTB button. Discord PTB version is an official Discord variant that differs from the standard Discord version distributed from the stable general channel in terms of update and download paths.

- **Repair Discord:** Completely removes Discord, clears Discord cache (logs you out of your account), performs ByeDPI installation and downloads and installs Discord from the official Discord site again.

- **Install Discord PTB:** If Discord PTB version is installed, removes it and downloads and installs Discord PTB version from the official Discord site.

- **Perform clean installation for Discord PTB:** If this option is active when the Install Discord PTB button is clicked, it removes the standard Discord while installing Discord PTB.

- **Status Controls:** Shows installed Discord versions and performs installation/removal and running operations.

**Note 2:** If you still experience problems after repair, you can test whether the problem is resolved by turning off your modem, waiting 15 seconds, then turning it back on. If your problem continues, you can create an error report from the Issues section of the Github page. The link to the Github page is available in the About section above.

---

## Advanced Page Usage

- **Services:** Shows the list of DPI bypass and tunneling related services installed by SplitWire-Turkey or by the user.

- **Apply DNS and DoH settings on every installation:** A system-wide DNS setting is automatically applied in all bypass method installations that can be performed within SplitWire-Turkey. Which method is used (DnsCrypt-Proxy or Google DNS/Quad9 with DoH) is determined by the **DNS Method** switch directly below. You can disable automatic DNS and DoH configuration (and therefore DnsCrypt-Proxy installation) entirely by turning off this switch.

- **DNS Method (DnsCrypt-Proxy / Windows DoH):** When enabled (and the DNS switch above is on), DnsCrypt-Proxy (encrypted DNS) is automatically installed and started on every setup/one-time start/blockcheck; your DNS server is pointed to 127.0.0.1 and ::1 (preventing plaintext leaks). If DnsCrypt-Proxy is already installed, it is not reinstalled. If this switch is turned off, native Windows DoH (Google DNS and Quad9) is used instead. The two methods are never used at the same time.

- **Remove All Services:** Removes all services in the list in the correct order, deletes drover files in the Discord folder and removes the WireSock Refresh Task Scheduler task.

- **Revert DNS and DoH Settings:** Resets the DNS and DoH settings made when any installation in SplitWire-Turkey is performed, setting the DNS setting to "Automatic (DHCP)" and the DoH setting to "Off".

- **Remove SplitWire-Turkey:** Reverts all changes made by SplitWire-Turkey and returns your system to its previous state, then starts the SplitWire-Turkey removal tool.

**Note:** WinDivert service cannot be removed without stopping Zapret or GoodbyeDPI services. Therefore, multiple confirmations may be requested.

---

## Language Options / Dil Seçenekleri / Варианты языка / Opciones de Idioma

- When you run SplitWire-Turkey, you can view language options and change the program's language using the language menu button located below the SplitWire-Turkey logo. Currently, Turkish, English, Русский and Español languages are available. [Click here to open English README file.](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_EN.md)

- SplitWire-Turkey'i çalıştırdığınızda SplitWire-Turkey logosunun altında bulunan dil menüsü butonu ile dil seçeneklerini görüp programın dilini dğeiştirebilirsiniz. Şuan için Türkçe, English, Русский ve Español dilleri mevcut. [Türkçe README dosyasını açmak için buraya tıklayın](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/README.md)

- При запуске SplitWire-Turkey вы можете просматривать языковые опции и изменять язык программы с помощью кнопки языкового меню, расположенной под логотипом SplitWire-Turkey. В настоящее время доступны турецкий, английский, русский и испанский языки. [Нажмите здесь, чтобы открыть файл README на русском языке.](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_RU.md)

- Al ejecutar SplitWire-Turkey, puede ver las opciones de idioma y cambiar el idioma del programa usando el botón del menú de idioma ubicado debajo del logotipo de SplitWire-Turkey. Actualmente, están disponibles los idiomas turco, inglés, ruso y español. [Haga clic aquí para abrir el archivo README en español.](https://github.com/cagritaskn/SplitWire-Turkey/blob/main/.github/README_ES.md)

---

## Important Notes

> [!CAUTION]
> If you are using an antivirus software other than Windows Defender, you may need to manually add rules to allow the executable files named "Program Files\SplitWire-Turkey\res\byedpi\ciadpi.exe" and "Program Files\SplitWire-Turkey\res\proxifyre\ProxiFyre.exe" in the firewall of the relevant antivirus software. For Windows Defender, firewall rules are added automatically, you don't need to do any extra operations. **If the antivirus software you use does not have its own network firewall feature or if you are not using an antivirus software other than Windows Defender, you can ignore this warning.**

> [!NOTE]
> Since the use of WinDivert files is blocked by the antivirus software named Kaspersky, you cannot use the GoodbyeDPI and Zapret tabs while Kaspersky is installed on your system. After completely removing Kaspersky from your system, download the **[SplitWire-Turkey Setup](https://github.com/cagritaskn/SplitWire-Turkey/releases/download/1.5.7/SplitWire-Turkey-Setup-Windows-1.5.7.exe)** file and perform installation again, these tabs will become active. You can also try to solve this problem by adding C:\Program Files\SplitWire-Turkey and C:\Users\-Username-\AppData\Local\SplitWire-Turkey folders to Kaspersky exceptions and downloading and installing SplitWire-Turkey again.

> [!NOTE]
> If you experience problems with WinDivert files in SplitWire-Turkey v1.5 and later versions for any reason, you can download and use the old version from [SplitWire-Turkey Release 1.0.0](https://github.com/cagritaskn/SplitWire-Turkey/releases/tag/1.0.0).

> [!NOTE]
> You can also check out our new project, **[SplitCord-Turkey](https://github.com/cagritaskn/SplitCord-Turkey)**.

---

## SplitWire-Turkey macOS Version

SplitWire-Turkey is currently only supported for Windows operating system. For macOS operating system, you can use the [SplitWire-Turkey-macOS](https://github.com/a-mertdincer/SplitWire-Turkey-macOS) application shared by [a-mertdincer](https://github.com/a-mertdincer).

---

## Possible Problems and Error Reporting
- "Register failed"/"Config file not found" error: Some internet providers or CloudFlare itself may block the use of its free API for various reasons. The most common reason for this is regional overuse abuse defined as "abusive usage". For this reason, wgcf cannot register and create a configuration file, and as a result, the "Register operation failed. Return code: 1" error is received. In such a case, unfortunately, the Standard Installation, Alternative Installation and Custom Installation methods cannot fulfill their function and the necessary configuration file cannot be created. Even if this ban can be bypassed temporarily using a VPN or proxy; the private-key and configuration file created temporarily tunneled from the Cloudflare API will only be valid for the tunneled machine, so it will still prevent usage. If you get this error, you can try using other methods.

- Error during service installations: Do not use this application while the Services window is open.

- Getting stuck on "Checking for updates" screen: Turn off your modem, wait 15-30 seconds, then restart it. Then restart your computer and test whether the problem is resolved. If it is not resolved, run SplitWire-Turkey, open the Repair tab and click the Repair Discord button. After restarting your computer, check if the problem is resolved. If you still can't get results, run SplitWire-Turkey, open the Repair tab and click the Install Discord PTB button, then after the installation is complete, run Discord PTB via Start > Discord PTB and check if the problem is resolved.

- Getting stuck on "Starting..." screen: Run SplitWire-Turkey, open the Repair tab and click the Repair Discord button. After restarting your computer, check if the problem is resolved. If you still can't get results, run SplitWire-Turkey, open the Repair tab and click the Install Discord PTB button, then after the installation is complete, run Discord PTB via Start > Discord PTB and check if the problem is resolved. If your problem is still not resolved, right-click on Update.exe in C:\Users\-Username-\AppData\Local\Discord\ location, select Properties, go to the Compatibility tab in the opened window, check the "Compatibility mode for this program:" box, select Windows 8, then click Apply and OK buttons, restart your computer and check if the problem is resolved. If your problem is still not resolved, apply the same step as before, but this time check the "Compatibility mode for this program:" box and select Windows 7, then click Apply and OK buttons, restart your computer and check if the problem is resolved.

- Discord "Messages could not be loaded" error: This problem occurs when Discord itself detects suspicious IP changes or when Cloudflare WARP detects abuse. If you experience this problem, turn off your modem, wait 15-30 seconds, then restart it. Then restart your computer and test whether the problem is resolved. If you still can't reach a solution this way, you can try resetting the Discord cache by deleting the C:\Users\-Username-\AppData\Roaming\discord folder. (This method will log you out of your Discord account, you will be asked to log in again) If you still can't reach a solution this way, try other methods.

- Creating error reports: You can go to the [SplitWire-Turkey Issues page](https://github.com/cagritaskn/SplitWire-Turkey/issues) and click the **New Issue** button in the top right, and report by adding the .log files in the AppData\Local\SplitWire-Turkey\Logs folder to your report. You can open the Logs folder using the Open Logs Folder button at the bottom of the About page of the SplitWire-Turkey program.

- If you keep experiencing issues with the Discord client itself, you can try our alternative project, **[SplitCord-Turkey](https://github.com/cagritaskn/SplitCord-Turkey)**.

---

## Removing SplitWire-Turkey from System and Reverting All Changes
There are many ways to remove **SplitWire-Turkey** from your system. These can be listed as using the **Remove SplitWire-Turkey** button in the **Advanced** tab within the program, using the **unins000.exe** removal package in the location where the program is installed, or finding **SplitWire-Turkey** in the Windows Add or Remove Programs window and clicking the Remove button from the options on the right. By following any of these paths, you can revert all changes and completely remove SplitWire-Turkey from your system.

> If you are using by downloading and extracting the ZIP file; After using the **Remove SplitWire-Turkey** button in the **Advanced** tab in **SplitWire-Turkey**, you can revert all changes and completely remove SplitWire-Turkey from your system using the folder where you extracted the ZIP file and the C:\Users\-Username-\AppData\Local\SplitWire-Turkey folder.

---

## Virus & SmartScreen Warning
Since the program is open source, you can view and examine all the code. The entire program is open source and the source code can be examined in the /src folder and recompiled if desired. Users who do not want to use the program and do not trust it are not obliged to use the program, using the program is at the user's discretion.
If you wish, you can scan the entire folder, installation file, .zip file or source codes on a site like [VirusTotal](https://www.virustotal.com/gui/home/upload) and examine the results, or if you know C# or have an acquaintance who knows it, you can consult to understand what the code is trying to do.

> [!NOTE]
> **SmartScreen "Windows protected your personal computer"** warning appears before running all unsigned software. The reason for this is that software must be subject to international code signing certificates. However, since this signing process requires regular payment based on the exchange rate and I am an independent developer who does not earn income, I cannot attempt to sign the software.

> [!NOTE]
> **[SplitWire-Turkey Setup file VirusTotal results](https://www.virustotal.com/gui/file-analysis/M2ZhNmIwYmNhODE2ZDdmZTdkY2I1YmJlY2ExNzViMzc6MTc4OTQxODE2NA==)** False positive virus or malware reports detected by antivirus software used by a small segment of users may be detected in the files, but these are software with unreliable detection methods. The reason for detection is that SplitWire-Turkey installs multiple applications from a single program and makes many changes on the system. (DNS changes, service and program package installation, removal, etc.) I recommend reading the notes given below for your concerns about Kaspersky.

> [!NOTE]
> **[SplitWire-Turkey ZIP file VirusTotal results](https://www.virustotal.com/gui/file-analysis/OGY5ZGQ1Mzc2MzIzYWE1YzdjNmY2OTEwOTcxMTA1OTg6MTc4OTQxODEwNQ==)** False positive virus or malware reports detected by antivirus software used by a small segment of users may be detected in the files, but these are software with unreliable detection methods. The reason for detection is that SplitWire-Turkey installs multiple applications from a single program and makes many changes on the system. (DNS changes, service and program package installation, removal, etc.) I recommend reading the notes given below for your concerns about Kaspersky.

> [!NOTE]
> **WinDivert** files are detected as RiskTool by Kaspersky and a few antivirus software. As can be understood from the warning name **not-a-virus:HEUR:RiskTool.Multi.WinDivert.gen**, these files are; **not a virus**, it says it is a tool that can be harmful when used with files downloaded from wrong sources. Since SplitWire-Turkey and all its plugins are open source, you can track and understand how the WinDivert library is used. If you look at the detection descriptions, you can see the word NotAVirus. This detection type is defined as a risk tool because the open source WinDivert library used by GoodbyeDPI and Zapret manipulates network packets on Windows. This library is open source and can be accessed from [WinDivert Github](https://github.com/basil00/WinDivert). Unfortunately, despite all the efforts of both Russian and Turkish software developers, Kaspersky, which is pro-Russian government, and a few antivirus software companies together with it did not accept the reports and objections, so you cannot run methods using WinDivert if the relevant antivirus software is installed on your system. You can remove Kaspersky and other false positive antivirus software from your system and perform installation again to run WinDivert methods, or you can download and use the old version without WinDivert from [SplitWire-Turkey Release 1.0.0](https://github.com/cagritaskn/SplitWire-Turkey/releases/tag/1.0.0).

> [!NOTE]
> **Not-a-virus warnings generally mean that an application can be misused when preferred.**
The not-a-virus:HEUR:RiskTool.Multi.WinDivertTool warning is such a warning.
WinDivert library is an open source library for manipulating network packets on Windows operating systems. This library gains functionality with various software. GoodbyeDPI is one of them. GoodbyeDPI's purpose in using the WinDivert library is to prevent the service provider from examining correctly by making small changes in network packets.
However, software that can use WinDivert for malicious purposes can also be written. For example, software that performs phishing, MITM attacks or recording/sending user inputs by completely changing packets can be prepared. **However, this does not make the WinDivert library malicious. The software that uses the WinDivert library for malicious purposes makes it malicious.**
The antivirus software named Kaspersky, whether right or wrong, warns about this, but the main issue comes from its submission to the pressures of the Russian government. As you know, there is an internet freedom restriction in Russia. The government puts pressure on companies under its roof to block bypass methods as much as possible. The company named Kaspersky does not resist these pressures and accepts them. It tries to prevent methods that help bypass in many ways.
**In short, as long as you download from the right source, SplitWire-Turkey cannot harm your computer. Every time you download, first look at the address bar and pay attention to the URL. Download and use SplitWire-Turkey only from [this page](https://github.com/cagritaskn/SplitWire-Turkey/releases/).**

---

## Thanks and Attributions

- I would like to thank **[Recep Baltaş](https://www.youtube.com/@Techolay/)**, founder of **[Techolay.net](https://techolay.net/sosyal/)**, who contributed to the development of the software.
- I would like to thank **[Bal Porsuğu](https://www.youtube.com/@sauali)** very much for the **[ByeDPI Split Tunneling method](https://www.youtube.com/watch?v=rkBL_kHBfm4)** guide, Zapret presets and all their efforts.
- **[wgcf](https://github.com/ViRb3/wgcf)** by **[ViRb3](https://github.com/ViRb3)**
- **[ProxiFyre](https://github.com/wiresock/proxifyre)** by **[Vadim Smirnov](https://github.com/wiresock)**
- **[ByeDPI](https://github.com/hufrea/byedpi)** by **[hufrea](https://github.com/hufrea/)**
- **[WireSock](https://www.wiresock.net/)** by **[Vadim Smirnov](https://github.com/wiresock)**
- **[drover](https://github.com/hdrover/discord-drover)** by **[hdrover](https://github.com/hdrover)**
- **[GoodbyeDPI](https://github.com/ValdikSS/GoodbyeDPI)** by **[ValdikSS](https://github.com/ValdikSS)**
- **[zapret](https://github.com/bol-van/zapret)** by **[bol-van](https://github.com/bol-van)**
- **[zapret2](https://github.com/bol-van/zapret2)** by **[bol-van](https://github.com/bol-van)**
- **[WinDivert](https://github.com/basil00/WinDivert)** by **[basil00](https://github.com/basil00)**
- **[SplitWire-Turkey-macOS](https://github.com/a-mertdincer/SplitWire-Turkey-macOS)** by **[a-mertdincer](https://github.com/a-mertdincer)**
- **I would like to thank other people who contributed to the project and Patreon and Github sponsors very much**

---

## How It Works

- Standard, Alternative and Custom Installation
First, a profile file is created with wgcf and this profile file is used with the WireSock client and split tunneling is started only for Discord.

- ByeDPI Split Tunneling and ByeDPI DLL Installation
First, the ByeDPI service is installed and in the ST method, this proxy is run for selected applications using ProxiFyre, in the DLL method, drover files ensure that Discord uses the proxy started by ByeDPI on localhost with automatic DLL injection.

- Zapret Automatic Installation
Finds ideal parameters for your system and internet provider using blockcheck technology and provides service installation by combining these parameters with your preferences. Scan speed selection adjusts how simple or deep the parameter scan will be.

- Zapret Preset Installation and One-time
Zapret service is installed or run once with predetermined ready settings (or edited versions if you made edits).

- Zapret2 Automatic Installation
Finds ideal parameters for your system and internet provider using blockcheck2 technology and provides service installation by combining these parameters with your preferences. Ready settings for well-known Turkish ISPs such as Türk Telekom, Superonline and Vodafone are tried automatically first; if one works, a full scan is not needed at all. Scan speed selection adjusts how simple or deep the parameter scan will be.

- Zapret2 Preset Installation and One-time
Zapret2 service is installed or run once with predetermined ready settings (or edited versions if you made edits).

- GoodbyeDPI Service Installation and One-time
GoodbyeDPI service is installed or run once with predetermined ready settings (or edited versions if you made edits). If the Use blacklist option is active, bypass is applied only for domains in the blacklist. (By default, it is set for Roblox, Discord and Wattpad)

- Remove All Services
The bypass services installed by SplitWire-Turkey or by the user are listed and all are removed in the correct order. After this operation, no bypass method remains on your system.

- DNS Method (DnsCrypt-Proxy / Windows DoH) and Revert DNS and DoH Settings
Before any installation you make in SplitWire-Turkey, all services are cleaned for a clean installation, then one of two methods (never both) is applied according to the **DNS Method** switch on the **Advanced** tab: when the switch is on, DnsCrypt-Proxy is installed and your DNS is pointed to 127.0.0.1 and ::1 (encrypted DNS); when the switch is off, Windows 11 supported DoH is activated and IPv4/IPv6 DNS assignment is made (Google primary, Quad9 secondary DNS; DoH is not supported on Windows 10 and below). The Revert DNS and DoH Settings button reverts all of these settings regardless of which method was used, returning DNS assignments to Automatic (DHCP) and turning off DoH.

- Remove SplitWire-Turkey
This button performs all cleanup operations and runs the unins000.exe removal package. When the operations started with this button are completed, SplitWire-Turkey becomes as if it was never installed on your system before.

---

## Recompiling

### Recompiling the Program Using C#
Requirements:
- **.NET 8.0 SDK** or higher
- **Visual Studio 2022** or **Visual Studio Code**
- **Windows 10/11** operating system

### Compilation Steps

1. **Download Source Code**
   ```bash
   git clone https://github.com/cagritaskn/SplitWire-Turkey.git
   cd SplitWire-Turkey/src
   ```

2. **Install Dependencies**
   ```bash
   cd SplitWireTurkey
   dotnet restore
   ```

3. **Compile the Application**
   ```bash
   # Simple compilation
   dotnet build -c Release
   
   # Or use batch script (Recommended)
   ..\build_simple.bat
   ```

### Recompiling Installation Executable Using InnoSetup
Requirements:
- **InnoSetup 6**
- **Windows 10/11** operating system

### Compilation Steps

1. **Compile C# Program and Go to the Folder Where Output SplitWire-Turkey.exe is Located**

2. **Copy Prerequisites Folder and Resources Folder and Their Contents to Your Current Folder** (It is not possible to upload Desktop Runtime files to the Prerequisites folder because it exceeds the file size limit. Instead, you must manually place windowsdesktop-runtime-6.0.35-win-x64.exe and windowsdesktop-runtime-6.0.35-win-x86.exe files in this folder.)

3. **Open a Command Line in Your Current Folder and Compile the Installation Executable**
   ```bash
   iscc "SplitWire-Turkey-Setup.iss"
   ```

---

## Copyright

```
Copyright © 2025 Çağrı Taşkın

This project is licensed under the MIT license.
See the LICENSE file for details.
```

---

## Donation and Support

Using this program is completely free. I do not earn any income from its use. However, you can support me from the donation addresses below so that I can continue my work. You can also leave a star for the project on Github (from the top of this page).

**GitHub Sponsor:**

[![Sponsor](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/cagritaskn)

**Patreon:**

[![Static Badge](https://img.shields.io/badge/cagritaskn-purple?logo=patreon&label=Patreon)](https://www.patreon.com/cagritaskn/membership)

---

## Disclaimer

**This software is created for educational purposes.**

- This tool is only for coding education and personal use
- It is not suitable for commercial use
- The developer is not responsible for any damage that may arise from the use of this software
- Users use this software at their own responsibility
- The selection of the program named Discord is necessary to test it on a program that is made inaccessible by DPI
- Compliance with legal regulations is the user's responsibility
> [!IMPORTANT]
> All legal responsibility arising from the use of this program belongs to the person using it. The application is written and edited only for educational and research purposes; using or not using this application under these conditions is the user's own choice. This project on the Github platform where open source codes are shared is written and edited for information sharing and coding education purposes.


