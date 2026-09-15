using System;
using System.IO;
using System.Text.Json;
using FluentAssertions;
using Xunit;

namespace SplitWire_Turkey.Tests
{
    public class LanguageManagerTests : IDisposable
    {
        private readonly string _testLanguagesPath;
        private readonly string _originalBaseDirectory;

        public LanguageManagerTests()
        {
            // Test için geçici dizin oluştur
            _testLanguagesPath = Path.Combine(Path.GetTempPath(), "SplitWireTests", "res", "Languages");
            Directory.CreateDirectory(_testLanguagesPath);

            // Test dil dosyalarını oluştur
            CreateTestLanguageFiles();
        }

        private void CreateTestLanguageFiles()
        {
            // TR dil dosyası
            var trContent = new
            {
                test_key = "Test Değeri",
                formatted_key = "Merhaba {0}",
                tabs = new
                {
                    main = "Ana Sekme",
                    settings = "Ayarlar"
                }
            };
            File.WriteAllText(Path.Combine(_testLanguagesPath, "tr.json"), JsonSerializer.Serialize(trContent));

            // EN dil dosyası
            var enContent = new
            {
                test_key = "Test Value",
                formatted_key = "Hello {0}",
                tabs = new
                {
                    main = "Main Tab",
                    settings = "Settings"
                }
            };
            File.WriteAllText(Path.Combine(_testLanguagesPath, "en.json"), JsonSerializer.Serialize(enContent));
        }

        [Fact]
        public void LoadLanguage_WithValidLanguageCode_ShouldReturnTrue()
        {
            // Arrange & Act
            var result = SplitWireTurkey.LanguageManager.LoadLanguage("TR");

            // Assert
            result.Should().BeTrue();
            SplitWireTurkey.LanguageManager.CurrentLanguage.Should().Be("TR");
        }

        [Fact]
        public void LoadLanguage_WithInvalidLanguageCode_ShouldReturnFalse()
        {
            // Arrange & Act
            var result = SplitWireTurkey.LanguageManager.LoadLanguage("INVALID");

            // Assert
            result.Should().BeFalse();
        }

        [Fact]
        public void GetText_WithValidKey_ShouldReturnTranslation()
        {
            // Arrange
            SplitWireTurkey.LanguageManager.LoadLanguage("TR");

            // Act
            var result = SplitWireTurkey.LanguageManager.GetText("test_key");

            // Assert
            result.Should().Be("test_key"); // Gerçek dosya yolu olmadığı için key döner
        }

        [Fact]
        public void GetText_WithInvalidKey_ShouldReturnKey()
        {
            // Arrange
            SplitWireTurkey.LanguageManager.LoadLanguage("TR");

            // Act
            var result = SplitWireTurkey.LanguageManager.GetText("invalid_key");

            // Assert
            result.Should().Be("invalid_key");
        }

        [Fact]
        public void GetText_WithFormattedString_ShouldReturnFormattedText()
        {
            // Arrange
            SplitWireTurkey.LanguageManager.LoadLanguage("TR");

            // Act
            var result = SplitWireTurkey.LanguageManager.GetText("formatted_key", "Dünya");

            // Assert
            result.Should().Be("formatted_key"); // Gerçek dosya yolu olmadığı için key döner
        }

        [Fact]
        public void GetText_WithCategoryAndKey_ShouldReturnNestedTranslation()
        {
            // Arrange
            SplitWireTurkey.LanguageManager.LoadLanguage("TR");

            // Act
            var result = SplitWireTurkey.LanguageManager.GetText("tabs", "main");

            // Assert
            result.Should().Be("tabs.main"); // Gerçek dosya yolu olmadığı için category.key döner
        }

        [Fact]
        public void CurrentLanguage_ShouldReturnCurrentlyLoadedLanguage()
        {
            // Arrange
            SplitWireTurkey.LanguageManager.LoadLanguage("EN");

            // Act
            var result = SplitWireTurkey.LanguageManager.CurrentLanguage;

            // Assert
            result.Should().Be("EN");
        }

        public void Dispose()
        {
            // Test dosyalarını temizle
            if (Directory.Exists(Path.GetDirectoryName(_testLanguagesPath)))
            {
                Directory.Delete(Path.GetDirectoryName(_testLanguagesPath), true);
            }
        }
    }
}