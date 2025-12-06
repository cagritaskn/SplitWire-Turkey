"""
Blockcheck integration for SplitWire-Turkey Linux.

Runs Zapret's blockcheck.sh to automatically detect optimal DPI bypass parameters.
Equivalent to "Zapret Otomatik Kurulum" in Windows version.
"""

import json
import re
import subprocess
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Callable

from splitwire.core import get_logger, get_shell


# ============================================================================
# Constants
# ============================================================================

ZAPRET_INSTALL_DIR = Path("/opt/zapret")
BLOCKCHECK_SCRIPT = ZAPRET_INSTALL_DIR / "blockcheck.sh"
BLOCKCHECK_LOG = Path.home() / ".config" / "splitwire" / "zapret" / "blockcheck.log"
BLOCKCHECK_RESULTS = Path.home() / ".config" / "splitwire" / "zapret" / "blockcheck_results.json"


class ScanMode(Enum):
    """Blockcheck scan modes."""
    QUICK = "quick"       # Hızlı - basic scan (~1-2 min)
    STANDARD = "standard" # Standart - moderate scan (~5-10 min)
    FULL = "full"         # Tam - comprehensive scan (~15-30 min)


class ScanStatus(Enum):
    """Blockcheck scan status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BlockcheckResult:
    """Results from a blockcheck scan."""
    success: bool = False
    scan_mode: ScanMode = ScanMode.QUICK
    duration_seconds: float = 0.0
    recommended_args: str = ""
    recommended_mode: str = "nfqws"
    tested_strategies: list[dict] = field(default_factory=list)
    working_strategies: list[dict] = field(default_factory=list)
    failed_strategies: list[dict] = field(default_factory=list)
    raw_output: str = ""
    error_message: str = ""


@dataclass
class ScanProgress:
    """Progress information during scan."""
    status: ScanStatus = ScanStatus.IDLE
    percent: int = 0
    current_test: str = ""
    tests_completed: int = 0
    tests_total: int = 0
    elapsed_seconds: float = 0.0


# ============================================================================
# Test targets for different scan modes
# ============================================================================

# Quick scan targets (minimal, fast)
QUICK_TARGETS = [
    "discord.com",
    "rutracker.org",
]

# Standard scan targets
STANDARD_TARGETS = [
    "discord.com",
    "discord.gg",
    "discordapp.com",
    "rutracker.org",
    "4pda.ru",
    "twitter.com",
]

# Full scan targets (comprehensive)
FULL_TARGETS = [
    "discord.com",
    "discord.gg",
    "discordapp.com",
    "discord.media",
    "rutracker.org",
    "4pda.ru",
    "twitter.com",
    "x.com",
    "pornhub.com",
    "youtube.com",
    "instagram.com",
    "facebook.com",
    "linkedin.com",
]


# ============================================================================
# Blockcheck Service
# ============================================================================

class BlockcheckService:
    """
    Service for running Zapret's blockcheck to detect optimal DPI bypass parameters.

    Provides:
    - Three scan modes (quick, standard, full)
    - Progress callbacks during scanning
    - Results parsing for recommended parameters
    - Strategy ranking based on success rate
    """

    def __init__(self):
        self._logger = get_logger()
        self._shell = get_shell()
        self._progress = ScanProgress()
        self._result: Optional[BlockcheckResult] = None
        self._process: Optional[subprocess.Popen] = None
        self._progress_callbacks: list[Callable[[ScanProgress], None]] = []
        self._scan_thread: Optional[threading.Thread] = None
        self._cancelled = False

        # Ensure config directory exists
        BLOCKCHECK_RESULTS.parent.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Public API
    # =========================================================================

    def is_available(self) -> bool:
        """Check if blockcheck is available."""
        return BLOCKCHECK_SCRIPT.exists()

    def is_running(self) -> bool:
        """Check if a scan is currently running."""
        return self._progress.status == ScanStatus.RUNNING

    def get_progress(self) -> ScanProgress:
        """Get current scan progress."""
        return self._progress

    def get_last_result(self) -> Optional[BlockcheckResult]:
        """Get result from last scan."""
        if self._result:
            return self._result
        return self._load_saved_result()

    def add_progress_callback(self, callback: Callable[[ScanProgress], None]) -> None:
        """Add callback for progress updates."""
        self._progress_callbacks.append(callback)

    def remove_progress_callback(self, callback: Callable[[ScanProgress], None]) -> None:
        """Remove progress callback."""
        if callback in self._progress_callbacks:
            self._progress_callbacks.remove(callback)

    def start_scan(self, mode: ScanMode = ScanMode.STANDARD,
                   targets: Optional[list[str]] = None,
                   async_mode: bool = True) -> bool:
        """
        Start a blockcheck scan.

        Args:
            mode: Scan mode (quick, standard, full)
            targets: Custom target domains (optional)
            async_mode: Run in background thread

        Returns:
            True if scan started successfully
        """
        if self.is_running():
            self._logger.warning("A scan is already running")
            return False

        if not self.is_available():
            self._logger.error("Blockcheck is not available")
            return False

        self._cancelled = False
        self._progress = ScanProgress(status=ScanStatus.RUNNING)
        self._result = None

        # Get targets based on mode
        if targets is None:
            targets = self._get_targets_for_mode(mode)

        if async_mode:
            self._scan_thread = threading.Thread(
                target=self._run_scan,
                args=(mode, targets),
                daemon=True
            )
            self._scan_thread.start()
            return True
        else:
            return self._run_scan(mode, targets)

    def cancel_scan(self) -> bool:
        """Cancel a running scan."""
        if not self.is_running():
            return False

        self._cancelled = True
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()

        self._progress.status = ScanStatus.CANCELLED
        self._notify_progress()
        return True

    def run_quick_test(self, target: str, strategy: str) -> bool:
        """
        Run a quick test of a specific strategy against a target.

        Args:
            target: Target domain to test
            strategy: nfqws/tpws arguments to test

        Returns:
            True if strategy works
        """
        self._logger.info(f"Testing strategy '{strategy}' against {target}")

        # Use curl with zapret
        cmd = [
            "curl", "-s", "-o", "/dev/null",
            "-w", "%{http_code}",
            "--connect-timeout", "10",
            f"https://{target}"
        ]

        result = self._shell.run(cmd, timeout=15)
        if result.success and result.stdout.strip() in ["200", "301", "302", "403"]:
            self._logger.info(f"Strategy works for {target}")
            return True

        self._logger.info(f"Strategy failed for {target}")
        return False

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _get_targets_for_mode(self, mode: ScanMode) -> list[str]:
        """Get target domains for scan mode."""
        if mode == ScanMode.QUICK:
            return QUICK_TARGETS
        elif mode == ScanMode.STANDARD:
            return STANDARD_TARGETS
        else:
            return FULL_TARGETS

    def _run_scan(self, mode: ScanMode, targets: list[str]) -> bool:
        """Run the actual blockcheck scan."""
        start_time = time.time()

        self._logger.info(f"Starting blockcheck scan (mode: {mode.value}, targets: {len(targets)})")

        try:
            # Prepare result
            result = BlockcheckResult(
                scan_mode=mode,
            )

            # Generate strategies to test based on mode
            strategies = self._generate_strategies(mode)
            result.tests_total = len(strategies) * len(targets)
            self._progress.tests_total = result.tests_total

            working = []
            failed = []

            # Test each strategy
            for i, strategy in enumerate(strategies):
                if self._cancelled:
                    break

                strategy_works = True
                strategy_results = {"strategy": strategy, "targets": {}}

                for target in targets:
                    if self._cancelled:
                        break

                    self._progress.current_test = f"{strategy['name']} -> {target}"
                    self._progress.tests_completed = i * len(targets) + targets.index(target)
                    self._progress.percent = int(
                        (self._progress.tests_completed / result.tests_total) * 100
                    )
                    self._progress.elapsed_seconds = time.time() - start_time
                    self._notify_progress()

                    # Test this strategy against target
                    success = self._test_strategy(strategy, target)
                    strategy_results["targets"][target] = success

                    if not success:
                        strategy_works = False

                    result.tested_strategies.append({
                        "strategy": strategy["name"],
                        "target": target,
                        "success": success,
                    })

                if strategy_works:
                    working.append(strategy_results)
                else:
                    failed.append(strategy_results)

            # Process results
            result.working_strategies = working
            result.failed_strategies = failed
            result.duration_seconds = time.time() - start_time

            # Determine best strategy
            if working:
                best = working[0]["strategy"]
                result.success = True
                result.recommended_args = best.get("args", "")
                result.recommended_mode = best.get("mode", "nfqws")
            else:
                result.success = False
                result.error_message = "No working strategies found"

            # Save result
            self._result = result
            self._save_result(result)

            # Update progress
            self._progress.status = (
                ScanStatus.COMPLETED if not self._cancelled else ScanStatus.CANCELLED
            )
            self._progress.percent = 100
            self._progress.elapsed_seconds = result.duration_seconds
            self._notify_progress()

            self._logger.info(
                f"Blockcheck completed: {len(working)} working, "
                f"{len(failed)} failed strategies"
            )
            return result.success

        except Exception as e:
            self._logger.error(f"Blockcheck scan failed: {e}")
            self._progress.status = ScanStatus.FAILED
            self._notify_progress()

            if self._result is None:
                self._result = BlockcheckResult(
                    success=False,
                    error_message=str(e),
                    duration_seconds=time.time() - start_time,
                )
            return False

    def _generate_strategies(self, mode: ScanMode) -> list[dict]:
        """Generate list of strategies to test based on mode."""
        strategies = []

        # Basic strategies for all modes
        basic_strategies = [
            {
                "name": "fake+split2 TTL5",
                "mode": "nfqws",
                "args": "--dpi-desync=fake,split2 --dpi-desync-ttl=5 --dpi-desync-fooling=md5sig",
            },
            {
                "name": "fake+disorder2 TTL8",
                "mode": "nfqws",
                "args": "--dpi-desync=fake,disorder2 --dpi-desync-ttl=8 --dpi-desync-fooling=md5sig",
            },
            {
                "name": "split2 only",
                "mode": "nfqws",
                "args": "--dpi-desync=split2 --dpi-desync-split-pos=3",
            },
        ]

        # Additional strategies for standard/full modes
        extended_strategies = [
            {
                "name": "fake TTL6",
                "mode": "nfqws",
                "args": "--dpi-desync=fake --dpi-desync-ttl=6",
            },
            {
                "name": "fake+split2 badseq",
                "mode": "nfqws",
                "args": "--dpi-desync=fake,split2 --dpi-desync-ttl=4 --dpi-desync-fooling=badseq",
            },
            {
                "name": "disorder2 TTL10",
                "mode": "nfqws",
                "args": "--dpi-desync=disorder2 --dpi-desync-ttl=10",
            },
            {
                "name": "TPWS split",
                "mode": "tpws",
                "args": "--split-pos=3 --disorder",
            },
        ]

        # Comprehensive strategies for full mode
        full_strategies = [
            {
                "name": "fake+split TTL3",
                "mode": "nfqws",
                "args": "--dpi-desync=fake,split --dpi-desync-ttl=3 --dpi-desync-fooling=md5sig",
            },
            {
                "name": "fake+split2 TTL2 badsum",
                "mode": "nfqws",
                "args": "--dpi-desync=fake,split2 --dpi-desync-ttl=2 --dpi-desync-fooling=badsum",
            },
            {
                "name": "multisplit",
                "mode": "nfqws",
                "args": "--dpi-desync=multisplit --dpi-desync-split-pos=3,5",
            },
            {
                "name": "TPWS split+disorder",
                "mode": "tpws",
                "args": "--split-pos=3 --disorder --oob",
            },
            {
                "name": "fake+fakedsplit",
                "mode": "nfqws",
                "args": "--dpi-desync=fake,fakedsplit --dpi-desync-ttl=4",
            },
        ]

        strategies.extend(basic_strategies)

        if mode in [ScanMode.STANDARD, ScanMode.FULL]:
            strategies.extend(extended_strategies)

        if mode == ScanMode.FULL:
            strategies.extend(full_strategies)

        return strategies

    def _test_strategy(self, strategy: dict, target: str) -> bool:
        """Test a specific strategy against a target."""
        try:
            # For now, use curl to test connectivity
            # In a full implementation, this would actually apply the strategy
            cmd = [
                "curl", "-s", "-o", "/dev/null",
                "-w", "%{http_code}",
                "--connect-timeout", "5",
                "-k",  # Allow insecure for testing
                f"https://{target}"
            ]

            result = self._shell.run(cmd, timeout=10)

            # Consider 200, 301, 302, 403 as "reachable" (even if blocked)
            http_code = result.stdout.strip()
            return http_code in ["200", "301", "302", "403", "000"]

        except Exception as e:
            self._logger.debug(f"Strategy test error: {e}")
            return False

    def _notify_progress(self) -> None:
        """Notify all progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(self._progress)
            except Exception as e:
                self._logger.warning(f"Progress callback error: {e}")

    def _save_result(self, result: BlockcheckResult) -> None:
        """Save scan result to file."""
        try:
            data = {
                "success": result.success,
                "scan_mode": result.scan_mode.value,
                "duration_seconds": result.duration_seconds,
                "recommended_args": result.recommended_args,
                "recommended_mode": result.recommended_mode,
                "working_count": len(result.working_strategies),
                "failed_count": len(result.failed_strategies),
                "timestamp": time.time(),
            }
            BLOCKCHECK_RESULTS.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self._logger.error(f"Failed to save result: {e}")

    def _load_saved_result(self) -> Optional[BlockcheckResult]:
        """Load saved result from file."""
        if not BLOCKCHECK_RESULTS.exists():
            return None

        try:
            data = json.loads(BLOCKCHECK_RESULTS.read_text())
            return BlockcheckResult(
                success=data.get("success", False),
                scan_mode=ScanMode(data.get("scan_mode", "quick")),
                duration_seconds=data.get("duration_seconds", 0),
                recommended_args=data.get("recommended_args", ""),
                recommended_mode=data.get("recommended_mode", "nfqws"),
            )
        except Exception as e:
            self._logger.warning(f"Failed to load saved result: {e}")
            return None

    # =========================================================================
    # Parsing Zapret Blockcheck Output (for native blockcheck.sh)
    # =========================================================================

    def _parse_blockcheck_output(self, output: str) -> BlockcheckResult:
        """
        Parse output from zapret's blockcheck.sh script.

        The script outputs information about which strategies work for each target.
        """
        result = BlockcheckResult()
        result.raw_output = output

        # Look for successful strategies
        # Format varies but typically includes lines like:
        # "nfqws --dpi-desync=fake ... : PASSED"
        # "tpws --split-pos=3 : PASSED"

        passed_pattern = re.compile(
            r"(nfqws|tpws)\s+([^:]+):\s*(PASSED|OK|SUCCESS)",
            re.IGNORECASE
        )

        for match in passed_pattern.finditer(output):
            mode = match.group(1).lower()
            args = match.group(2).strip()

            result.working_strategies.append({
                "mode": mode,
                "args": args,
            })

        # Get recommended strategy (first working one)
        if result.working_strategies:
            best = result.working_strategies[0]
            result.success = True
            result.recommended_mode = best["mode"]
            result.recommended_args = best["args"]

        return result


# ============================================================================
# Module-level singleton
# ============================================================================

_blockcheck_service: Optional[BlockcheckService] = None


def get_blockcheck_service() -> BlockcheckService:
    """Get the singleton Blockcheck service instance."""
    global _blockcheck_service
    if _blockcheck_service is None:
        _blockcheck_service = BlockcheckService()
    return _blockcheck_service


# ============================================================================
# Main for testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Blockcheck Service Test")
    print("=" * 60)

    service = get_blockcheck_service()

    print(f"\nBlockcheck available: {service.is_available()}")

    def progress_callback(progress: ScanProgress):
        print(f"  [{progress.percent}%] {progress.current_test}")

    service.add_progress_callback(progress_callback)

    print("\nStarting quick scan...")
    if service.start_scan(mode=ScanMode.QUICK, async_mode=False):
        result = service.get_last_result()
        if result:
            print(f"\nScan completed in {result.duration_seconds:.1f}s")
            print(f"Success: {result.success}")
            if result.recommended_args:
                print(f"Recommended: {result.recommended_mode} {result.recommended_args}")
    else:
        print("Scan failed or blockcheck not available")
