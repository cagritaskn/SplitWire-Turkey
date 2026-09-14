using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Collections.Generic; // Added missing import

namespace SplitWireTurkey.Services
{
    public class WireGuardService
    {
        private readonly string _wgcfPath;
        private readonly string _resDir;

        public WireGuardService()
        {
            _resDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "res");
            _wgcfPath = Path.Combine(_resDir, "wgcf.exe");
            
            if (!Directory.Exists(_resDir))
                Directory.CreateDirectory(_resDir);
        }

        public async Task<bool> CreateProfileAsync(string[] extraFolders = null, bool includeBrowsers = false)
        {
            try
            {
                var wgcfPath = await DownloadWgcfAsync();
                if (string.IsNullOrEmpty(wgcfPath))
                {
                    System.Windows.MessageBox.Show(LanguageManager.GetText("messages", "wgcf_download_failed"), LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                    return false;
                }

                // Remove existing account file if it exists
                var accountFile = Path.Combine(_resDir, "wgcf-account.toml");
                if (File.Exists(accountFile))
                {
                    try { File.Delete(accountFile); } catch { }
                }

                // Register with wgcf
                var registerResult = await ExecuteCommandAsync(_wgcfPath, "register --accept-tos");
                
                if (registerResult != 0)
                {
                    // Check if files were created despite the error
                    if (CheckWgcfFilesExist())
                    {
                        // Files exist, continue with the process despite the error
                        Debug.WriteLine($"Register returned {registerResult} but files exist, continuing...");
                    }
                    else
                    {
                        // Even if files don't exist, continue without showing error
                        Debug.WriteLine($"Register returned {registerResult} and files don't exist, but continuing anyway...");
                    }
                }

                // Generate profile
                var generateResult = await ExecuteCommandAsync(_wgcfPath, "generate");
                
                // Check if profile file was created despite the error
                if (generateResult != 0)
                {
                    if (CheckWgcfFilesExist())
                    {
                        // Profile file exists, continue with the process despite the error
                        Debug.WriteLine($"Generate returned {generateResult} but profile file exists, continuing...");
                    }
                    else
                    {
                        // Even if files don't exist, continue without showing error
                        Debug.WriteLine($"Generate returned {generateResult} and files don't exist, but continuing anyway...");
                    }
                }

                // Modify configuration
                var profilePath = Path.Combine(_resDir, "wgcf-profile.conf");
                if (File.Exists(profilePath))
                {
                    return await ModifyConfigurationAsync(profilePath, extraFolders, includeBrowsers);
                }
                else
                {
                    MessageBox.Show(LanguageManager.GetText("messages", "profile_not_found"), 
                        LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                    return false;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(string.Format(LanguageManager.GetText("messages", "profile_creation_error"), ex.Message), 
                    LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                return false;
            }
        }

        private async Task<bool> ModifyConfigurationAsync(string profilePath, string[] extraFolders, bool includeBrowsers = false)
        {
            try
            {
                var lines = await File.ReadAllLinesAsync(profilePath);
                var newLines = new List<string>();
                var username = Environment.UserName;
                var discordPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Discord");

                var appPaths = new List<string>
                {
                    discordPath,
                    "discord",
                    "roblox",
                    "Discord.exe",
                    "DiscordPTB.exe",
                    "SplitCord-Turkey.exe",
                    "SplitWire-Turkey.exe",
                    "Update.exe",
                    "RobloxPlayerBeta.exe",
                    "RobloxPlayerInstaller.exe"
                };

                // Tarayıcı uygulamalarını ekle (eğer isteniyorsa)
                if (includeBrowsers)
                {
                    var browserApps = new[]
                    {
                        "browser.exe",
                        "chrome.exe",
                        "firefox.exe",
                        "opera.exe",
                        "operagx.exe",
                        "brave.exe",
                        "vivaldi.exe",
                        "msedge.exe",
                        "zen.exe",
                        "chromium.exe",
                        "iexplore.exe",
                        "Maxthon.exe",
                        "librewolf.exe",
                        "electron.exe"
                    };
                    appPaths.AddRange(browserApps);
                }

                if (extraFolders != null)
                {
                    foreach (var folder in extraFolders)
                    {
                        if (!string.IsNullOrWhiteSpace(folder))
                            appPaths.Add(folder.Trim());
                    }
                }

                var allowedAppsLine = $"AllowedApps = {string.Join(", ", appPaths)}";

                foreach (var line in lines)
                {
                    newLines.Add(line);
                    if (line.Trim().StartsWith("Endpoint"))
                    {
                        newLines.Add(allowedAppsLine);
                    }
                }

                await File.WriteAllLinesAsync(profilePath, newLines);
                return true;
            }
            catch (Exception ex)
            {
                MessageBox.Show(string.Format(LanguageManager.GetText("messages", "config_edit_error"), ex.Message), 
                    LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                return false;
            }
        }

        private async Task<int> ExecuteCommandAsync(string command, string arguments)
        {
            return await Task.Run(() =>
            {
                try
                {
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = command,
                        Arguments = arguments,
                        WorkingDirectory = _resDir,
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };

                    using var process = new Process { StartInfo = startInfo };
                    process.Start();
                    
                    var output = process.StandardOutput.ReadToEnd();
                    var error = process.StandardError.ReadToEnd();
                    process.WaitForExit();
                    
                    // Log the command execution details
                    Debug.WriteLine($"Command: {command} {arguments}");
                    Debug.WriteLine($"Working Directory: {_resDir}");
                    Debug.WriteLine($"Exit Code: {process.ExitCode}");
                    Debug.WriteLine($"Output: {output}");
                    if (!string.IsNullOrEmpty(error))
                    {
                        Debug.WriteLine($"Error: {error}");
                    }
                    
                    return process.ExitCode;
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"Command execution failed: {ex.Message}");
                    return -1;
                }
            });
        }

        public string GetConfigPath()
        {
            return Path.Combine(_resDir, "wgcf-profile.conf");
        }

        public bool CheckWgcfFilesExist()
        {
            var accountFile = Path.Combine(_resDir, "wgcf-account.toml");
            var profileFile = Path.Combine(_resDir, "wgcf-profile.conf");
            
            var accountExists = File.Exists(accountFile);
            var profileExists = File.Exists(profileFile);
            
            Debug.WriteLine($"wgcf-account.toml exists: {accountExists}");
            Debug.WriteLine($"wgcf-profile.conf exists: {profileExists}");
            
            return accountExists && profileExists;
        }

        private async Task<string> DownloadWgcfAsync()
        {
            try
            {
                // Check if wgcf.exe already exists and is not too old (7 days)
                if (File.Exists(_wgcfPath))
                {
                    var fileInfo = new FileInfo(_wgcfPath);
                    if (DateTime.Now.Subtract(fileInfo.CreationTime).TotalDays < 7)
                    {
                        Debug.WriteLine("Using existing wgcf.exe (less than 7 days old)");
                        return _wgcfPath;
                    }
                }

                // Download latest release info from GitHub
                using (var client = new System.Net.Http.HttpClient())
                {
                    client.DefaultRequestHeaders.Add("User-Agent", "SplitWire-Turkey");
                    
                    // Get latest release info
                    var releasesUrl = "https://api.github.com/repos/ViRb3/wgcf/releases/latest";
                    var releasesResponse = await client.GetStringAsync(releasesUrl);
                    
                    // Parse JSON to find Windows AMD64 asset
                    var assetMatch = System.Text.RegularExpressions.Regex.Match(releasesResponse, 
                        @"""browser_download_url"":\s*""([^""]*wgcf_[^""]*_windows_amd64[^""]*)""");
                    
                    if (!assetMatch.Success)
                    {
                        Debug.WriteLine("Windows AMD64 version not found in GitHub releases");
                        // Try to use existing file if available
                        if (File.Exists(_wgcfPath))
                        {
                            Debug.WriteLine("Using existing wgcf.exe as fallback");
                            return _wgcfPath;
                        }
                        else
                        {
                            System.Windows.MessageBox.Show(LanguageManager.GetText("messages", "wgcf_version_not_found"), 
                                LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                            return null;
                        }
                    }

                    var downloadUrl = assetMatch.Groups[1].Value;
                    
                    // Download the file
                    var response = await client.GetAsync(downloadUrl);
                    response.EnsureSuccessStatusCode();
                    
                    using (var fileStream = File.Create(_wgcfPath))
                    {
                        await response.Content.CopyToAsync(fileStream);
                    }
                }

                return _wgcfPath;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"wgcf.exe download failed: {ex.Message}");
                
                // Try to use existing file if available
                if (File.Exists(_wgcfPath))
                {
                    Debug.WriteLine("Using existing wgcf.exe as fallback after download failure");
                    return _wgcfPath;
                }
                else
                {
                    System.Windows.MessageBox.Show(string.Format(LanguageManager.GetText("messages", "wgcf_download_error"), ex.Message), 
                        LanguageManager.GetText("messages", "unexpected_error_title"), MessageBoxButton.OK, MessageBoxImage.Error);
                    return null;
                }
            }
        }
    }
} 