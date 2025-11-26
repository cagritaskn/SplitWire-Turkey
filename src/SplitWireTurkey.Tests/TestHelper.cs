using System;
using System.IO;

namespace SplitWire_Turkey.Tests
{
    /// <summary>
    /// Test yardımcı sınıfı
    /// </summary>
    public static class TestHelper
    {
        /// <summary>
        /// Test için geçici dizin oluşturur
        /// </summary>
        public static string CreateTempDirectory(string prefix = "SplitWireTest")
        {
            var tempPath = Path.Combine(Path.GetTempPath(), $"{prefix}_{Guid.NewGuid():N}");
            Directory.CreateDirectory(tempPath);
            return tempPath;
        }

        /// <summary>
        /// Test dizinini temizler
        /// </summary>
        public static void CleanupTempDirectory(string path)
        {
            try
            {
                if (Directory.Exists(path))
                {
                    Directory.Delete(path, true);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Temp directory cleanup failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Test için geçici dosya oluşturur
        /// </summary>
        public static string CreateTempFile(string content = "", string extension = ".tmp")
        {
            var tempFile = Path.GetTempFileName();
            if (!string.IsNullOrEmpty(extension) && !tempFile.EndsWith(extension))
            {
                var newTempFile = Path.ChangeExtension(tempFile, extension);
                File.Move(tempFile, newTempFile);
                tempFile = newTempFile;
            }

            if (!string.IsNullOrEmpty(content))
            {
                File.WriteAllText(tempFile, content);
            }

            return tempFile;
        }

        /// <summary>
        /// Geçerli bir sürüm string'i olup olmadığını kontrol eder
        /// </summary>
        public static bool IsValidVersionString(string version)
        {
            return Version.TryParse(version, out _);
        }

        /// <summary>
        /// Test için mock dil dosyası oluşturur
        /// </summary>
        public static string CreateMockLanguageFile(string languageCode, object content)
        {
            var tempDir = CreateTempDirectory("LanguageTest");
            var languagesDir = Path.Combine(tempDir, "res", "Languages");
            Directory.CreateDirectory(languagesDir);

            var filePath = Path.Combine(languagesDir, $"{languageCode.ToLower()}.json");
            var jsonContent = System.Text.Json.JsonSerializer.Serialize(content);
            File.WriteAllText(filePath, jsonContent);

            return tempDir;
        }
    }
}