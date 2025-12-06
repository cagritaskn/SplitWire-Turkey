"""
Tests for the Blockcheck integration module.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from splitwire.services.blockcheck import (
    BlockcheckService,
    BlockcheckResult,
    ScanMode,
    ScanStatus,
    ScanProgress,
    get_blockcheck_service,
    QUICK_TARGETS,
    STANDARD_TARGETS,
    FULL_TARGETS,
)


class TestScanMode:
    """Tests for ScanMode enum."""

    def test_mode_values(self):
        """Test all mode values exist."""
        assert ScanMode.QUICK.value == "quick"
        assert ScanMode.STANDARD.value == "standard"
        assert ScanMode.FULL.value == "full"

    def test_mode_count(self):
        """Test all expected modes are defined."""
        assert len(ScanMode) == 3


class TestScanStatus:
    """Tests for ScanStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert ScanStatus.IDLE.value == "idle"
        assert ScanStatus.RUNNING.value == "running"
        assert ScanStatus.COMPLETED.value == "completed"
        assert ScanStatus.FAILED.value == "failed"
        assert ScanStatus.CANCELLED.value == "cancelled"

    def test_status_count(self):
        """Test all expected statuses are defined."""
        assert len(ScanStatus) == 5


class TestBlockcheckResult:
    """Tests for BlockcheckResult dataclass."""

    def test_default_result(self):
        """Test default result values."""
        result = BlockcheckResult()
        assert result.success is False
        assert result.scan_mode == ScanMode.QUICK
        assert result.duration_seconds == 0.0
        assert result.recommended_args == ""
        assert result.working_strategies == []

    def test_successful_result(self):
        """Test successful result."""
        result = BlockcheckResult(
            success=True,
            scan_mode=ScanMode.STANDARD,
            duration_seconds=120.5,
            recommended_args="--dpi-desync=fake,split2",
            recommended_mode="nfqws",
            working_strategies=[
                {"strategy": "fake+split2", "targets": {"discord.com": True}},
            ],
        )
        assert result.success is True
        assert result.scan_mode == ScanMode.STANDARD
        assert len(result.working_strategies) == 1


class TestScanProgress:
    """Tests for ScanProgress dataclass."""

    def test_default_progress(self):
        """Test default progress values."""
        progress = ScanProgress()
        assert progress.status == ScanStatus.IDLE
        assert progress.percent == 0
        assert progress.current_test == ""
        assert progress.tests_completed == 0

    def test_progress_update(self):
        """Test progress with values."""
        progress = ScanProgress(
            status=ScanStatus.RUNNING,
            percent=50,
            current_test="Testing fake+split2 -> discord.com",
            tests_completed=10,
            tests_total=20,
            elapsed_seconds=60.0,
        )
        assert progress.status == ScanStatus.RUNNING
        assert progress.percent == 50


class TestTargetLists:
    """Tests for target domain lists."""

    def test_quick_targets(self):
        """Test QUICK_TARGETS list."""
        assert isinstance(QUICK_TARGETS, list)
        assert len(QUICK_TARGETS) >= 1
        assert "discord.com" in QUICK_TARGETS

    def test_standard_targets(self):
        """Test STANDARD_TARGETS list."""
        assert isinstance(STANDARD_TARGETS, list)
        assert len(STANDARD_TARGETS) > len(QUICK_TARGETS)
        # Standard includes quick targets
        for target in QUICK_TARGETS:
            assert target in STANDARD_TARGETS

    def test_full_targets(self):
        """Test FULL_TARGETS list."""
        assert isinstance(FULL_TARGETS, list)
        assert len(FULL_TARGETS) > len(STANDARD_TARGETS)
        # Full includes standard targets
        for target in STANDARD_TARGETS:
            assert target in FULL_TARGETS


class TestBlockcheckService:
    """Tests for BlockcheckService class."""

    @pytest.fixture
    def service(self):
        """Create a Blockcheck service instance."""
        with patch('splitwire.services.blockcheck.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.blockcheck.get_shell') as mock_shell:
                mock_shell.return_value = MagicMock()
                with patch('splitwire.services.blockcheck.BLOCKCHECK_RESULTS', Path(tempfile.mktemp())):
                    service = BlockcheckService()
                    return service

    def test_initial_state(self, service):
        """Test initial service state."""
        assert not service.is_running()
        progress = service.get_progress()
        assert progress.status == ScanStatus.IDLE

    def test_is_available_no_script(self, service):
        """Test availability when script doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            assert not service.is_available()

    def test_is_available_with_script(self, service):
        """Test availability when script exists."""
        with patch('splitwire.services.blockcheck.BLOCKCHECK_SCRIPT') as mock_path:
            mock_path.exists.return_value = True
            assert service.is_available()

    def test_get_targets_for_mode(self, service):
        """Test getting targets for each mode."""
        quick = service._get_targets_for_mode(ScanMode.QUICK)
        standard = service._get_targets_for_mode(ScanMode.STANDARD)
        full = service._get_targets_for_mode(ScanMode.FULL)

        assert quick == QUICK_TARGETS
        assert standard == STANDARD_TARGETS
        assert full == FULL_TARGETS

    def test_progress_callbacks(self, service):
        """Test progress callback mechanism."""
        received_progress = []

        def callback(progress):
            received_progress.append(progress)

        service.add_progress_callback(callback)
        service._notify_progress()

        assert len(received_progress) == 1

        service.remove_progress_callback(callback)
        service._notify_progress()

        assert len(received_progress) == 1  # No new callback


class TestBlockcheckStrategies:
    """Tests for strategy generation."""

    @pytest.fixture
    def service(self):
        """Create a Blockcheck service instance."""
        with patch('splitwire.services.blockcheck.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.blockcheck.get_shell') as mock_shell:
                mock_shell.return_value = MagicMock()
                service = BlockcheckService()
                return service

    def test_generate_strategies_quick(self, service):
        """Test strategy generation for quick mode."""
        strategies = service._generate_strategies(ScanMode.QUICK)
        assert isinstance(strategies, list)
        assert len(strategies) >= 3  # At least basic strategies

        # Check structure
        for strategy in strategies:
            assert "name" in strategy
            assert "mode" in strategy
            assert "args" in strategy

    def test_generate_strategies_standard(self, service):
        """Test strategy generation for standard mode."""
        quick_strategies = service._generate_strategies(ScanMode.QUICK)
        standard_strategies = service._generate_strategies(ScanMode.STANDARD)

        # Standard should have more strategies than quick
        assert len(standard_strategies) > len(quick_strategies)

    def test_generate_strategies_full(self, service):
        """Test strategy generation for full mode."""
        standard_strategies = service._generate_strategies(ScanMode.STANDARD)
        full_strategies = service._generate_strategies(ScanMode.FULL)

        # Full should have most strategies
        assert len(full_strategies) > len(standard_strategies)

    def test_strategies_have_nfqws_and_tpws(self, service):
        """Test that both nfqws and tpws strategies exist."""
        strategies = service._generate_strategies(ScanMode.FULL)

        nfqws_count = sum(1 for s in strategies if s["mode"] == "nfqws")
        tpws_count = sum(1 for s in strategies if s["mode"] == "tpws")

        assert nfqws_count > 0
        assert tpws_count > 0


class TestBlockcheckResultPersistence:
    """Tests for result save/load."""

    def test_save_and_load_result(self):
        """Test saving and loading results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results_file = Path(tmpdir) / "results.json"

            with patch('splitwire.services.blockcheck.get_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                with patch('splitwire.services.blockcheck.get_shell') as mock_shell:
                    mock_shell.return_value = MagicMock()
                    with patch('splitwire.services.blockcheck.BLOCKCHECK_RESULTS', results_file):
                        service = BlockcheckService()

                        # Create and save result
                        result = BlockcheckResult(
                            success=True,
                            scan_mode=ScanMode.STANDARD,
                            duration_seconds=60.0,
                            recommended_args="--dpi-desync=fake",
                            recommended_mode="nfqws",
                        )
                        service._save_result(result)

                        # Verify file exists
                        assert results_file.exists()

                        # Load and verify
                        loaded = service._load_saved_result()
                        assert loaded is not None
                        assert loaded.success is True
                        assert loaded.scan_mode == ScanMode.STANDARD
                        assert loaded.recommended_args == "--dpi-desync=fake"


class TestBlockcheckCancellation:
    """Tests for scan cancellation."""

    @pytest.fixture
    def service(self):
        """Create a Blockcheck service instance."""
        with patch('splitwire.services.blockcheck.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.blockcheck.get_shell') as mock_shell:
                mock_shell.return_value = MagicMock()
                service = BlockcheckService()
                return service

    def test_cancel_when_not_running(self, service):
        """Test cancellation when not running."""
        result = service.cancel_scan()
        assert result is False

    def test_cancel_during_scan(self, service):
        """Test cancellation during scan."""
        # Simulate running state
        service._progress.status = ScanStatus.RUNNING

        result = service.cancel_scan()
        assert result is True
        assert service._cancelled is True


class TestBlockcheckSingleton:
    """Tests for singleton pattern."""

    def test_get_blockcheck_service_singleton(self):
        """Test that get_blockcheck_service returns singleton."""
        import splitwire.services.blockcheck as bc_module
        bc_module._blockcheck_service = None

        service1 = get_blockcheck_service()
        service2 = get_blockcheck_service()
        assert service1 is service2


class TestBlockcheckQuickTest:
    """Tests for quick test functionality."""

    @pytest.fixture
    def service(self):
        """Create a Blockcheck service instance."""
        with patch('splitwire.services.blockcheck.get_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            with patch('splitwire.services.blockcheck.get_shell') as mock_shell:
                mock_instance = MagicMock()
                mock_shell.return_value = mock_instance
                service = BlockcheckService()
                return service

    def test_run_quick_test_success(self, service):
        """Test quick test with successful result."""
        service._shell.run.return_value = MagicMock(
            success=True,
            stdout="200"
        )

        result = service.run_quick_test("discord.com", "--dpi-desync=fake")
        assert result is True

    def test_run_quick_test_failure(self, service):
        """Test quick test with failed result."""
        service._shell.run.return_value = MagicMock(
            success=False,
            stdout=""
        )

        result = service.run_quick_test("discord.com", "--dpi-desync=fake")
        assert result is False
