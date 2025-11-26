using System;
using System.IO;
using FluentAssertions;
using Xunit;

namespace SplitWire_Turkey.Tests
{
    public class IntegrationTests
    {
        [Fact]
        public void Application_ShouldHaveValidConfiguration()
        {
            // Arrange
            var baseDirectory = AppDomain.CurrentDomain.BaseDirectory;

            // Act & Assert
            baseDirectory.Should().NotBeNullOrEmpty();
            Directory.Exists(baseDirectory).Should().BeTrue();
        }

        [Fact]
        public void LanguageManager_ShouldInitializeWithDefaultLanguage()
        {
            // Act
            var currentLanguage = SplitWireTurkey.LanguageManager.CurrentLanguage;

            // Assert
            currentLanguage.Should().NotBeNullOrEmpty();
            currentLanguage.Should().Be("TR"); // Default language should be Turkish
        }

        [Fact]
        public void VersionHelper_AllVersionMethods_ShouldReturnValidVersions()
        {
            // Act
            var assemblyVersion = SplitWireTurkey.VersionHelper.GetAssemblyVersion();
            var fileVersion = SplitWireTurkey.VersionHelper.GetFileVersion();
            var productVersion = SplitWireTurkey.VersionHelper.GetProductVersion();

            // Assert
            assemblyVersion.Should().NotBeNullOrEmpty();
            fileVersion.Should().NotBeNullOrEmpty();
            productVersion.Should().NotBeNullOrEmpty();

            // All versions should be valid version strings
            Version.TryParse(assemblyVersion, out _).Should().BeTrue();
            Version.TryParse(fileVersion, out _).Should().BeTrue();
            
            // Product version might have additional info, so just check if it starts with a valid version
            var productVersionParts = productVersion.Split('-', '+');
            Version.TryParse(productVersionParts[0], out _).Should().BeTrue();
        }

        [Theory]
        [InlineData("TR")]
        [InlineData("EN")]
        [InlineData("RU")]
        public void LanguageManager_ShouldHandleSupportedLanguages(string languageCode)
        {
            // Act
            var result = SplitWireTurkey.LanguageManager.LoadLanguage(languageCode);

            // Assert
            // Even if the language file doesn't exist, the method should handle it gracefully
            SplitWireTurkey.LanguageManager.CurrentLanguage.Should().Be(languageCode);
        }

        [Fact]
        public void LanguageManager_GetText_ShouldHandleNullAndEmptyKeys()
        {
            // Arrange
            SplitWireTurkey.LanguageManager.LoadLanguage("TR");

            // Act & Assert
            var emptyResult = SplitWireTurkey.LanguageManager.GetText("");
            var nullResult = SplitWireTurkey.LanguageManager.GetText(null);

            emptyResult.Should().Be("");
            nullResult.Should().BeNull();
        }

        [Fact]
        public void Application_ShouldHaveCorrectAssemblyInfo()
        {
            // Act
            var assembly = System.Reflection.Assembly.GetAssembly(typeof(SplitWireTurkey.VersionHelper));

            // Assert
            assembly.Should().NotBeNull();
            assembly.GetName().Name.Should().Be("SplitWire-Turkey");
        }
    }
}