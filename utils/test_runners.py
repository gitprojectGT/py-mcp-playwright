"""
Test execution utilities and custom runners.
"""

import os
import sys
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path


class TestRunner:
    """Custom test runner with additional functionality."""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.results = {}
    
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests only."""
        return self._run_pytest(["-m", "smoke", "-v"])
    
    def run_api_tests(self) -> Dict[str, Any]:
        """Run API tests only."""
        return self._run_pytest(["-m", "api", "-v"])
    
    def run_ui_tests(self) -> Dict[str, Any]:
        """Run UI tests only.""" 
        return self._run_pytest(["-m", "ui", "-v"])
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests only."""
        return self._run_pytest(["-m", "integration", "-v"])
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        return self._run_pytest(["-m", "slow", "-v", "--tb=short"])
    
    def run_parallel_tests(self, workers: int = 4) -> Dict[str, Any]:
        """Run tests in parallel."""
        return self._run_pytest(["-n", str(workers), "-v"])
    
    def run_with_coverage(self, min_coverage: int = 80) -> Dict[str, Any]:
        """Run tests with coverage reporting."""
        args = [
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            f"--cov-fail-under={min_coverage}",
            "-v"
        ]
        return self._run_pytest(args)
    
    def run_browser_specific_tests(self, browser: str) -> Dict[str, Any]:
        """Run tests for specific browser."""
        env = os.environ.copy()
        env["PLAYWRIGHT_BROWSER"] = browser
        return self._run_pytest(["-v"], env=env)
    
    def _run_pytest(self, args: List[str], env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute pytest with given arguments."""
        cmd = [sys.executable, "-m", "pytest"] + args
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                env=env or os.environ.copy()
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(cmd)
            }


class ContinuousTestRunner:
    """Runner for continuous testing scenarios."""
    
    def __init__(self, test_dir: str = "tests"):
        self.test_dir = Path(test_dir)
        self.runner = TestRunner()
    
    def watch_and_run(self, patterns: List[str] = None) -> None:
        """Watch for file changes and run tests."""
        try:
            import watchdog
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            print("watchdog package required for file watching. Install with: pip install watchdog")
            return
        
        patterns = patterns or ["*.py"]
        
        class TestEventHandler(FileSystemEventHandler):
            def __init__(self, runner):
                self.runner = runner
            
            def on_modified(self, event):
                if not event.is_directory and any(event.src_path.endswith(p.replace("*", "")) for p in patterns):
                    print(f"File changed: {event.src_path}")
                    print("Running tests...")
                    result = self.runner.run_smoke_tests()
                    if result["success"]:
                        print("✅ Tests passed!")
                    else:
                        print("❌ Tests failed!")
                        print(result.get("stderr", ""))
        
        event_handler = TestEventHandler(self.runner)
        observer = Observer()
        observer.schedule(event_handler, str(self.test_dir), recursive=True)
        observer.start()
        
        try:
            print(f"Watching {self.test_dir} for changes... Press Ctrl+C to stop.")
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\nStopped watching for changes.")
        
        observer.join()


def create_test_report(results: Dict[str, Any], output_file: str = "test-report.html") -> None:
    """Create HTML test report."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            .info {{ color: blue; }}
            pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Test Execution Report</h1>
        <h2>Summary</h2>
        <p class="{status_class}">Status: {status}</p>
        <p>Return Code: {returncode}</p>
        <p>Command: <code>{command}</code></p>
        
        <h2>Output</h2>
        <pre>{stdout}</pre>
        
        {stderr_section}
    </body>
    </html>
    """
    
    status = "PASSED" if results.get("success") else "FAILED"
    status_class = "success" if results.get("success") else "failure"
    
    stderr_section = ""
    if results.get("stderr"):
        stderr_section = f"""
        <h2>Errors</h2>
        <pre class="failure">{results['stderr']}</pre>
        """
    
    html_content = html_template.format(
        status=status,
        status_class=status_class,
        returncode=results.get("returncode", "N/A"),
        command=results.get("command", "N/A"),
        stdout=results.get("stdout", "No output"),
        stderr_section=stderr_section
    )
    
    with open(output_file, "w") as f:
        f.write(html_content)
    
    print(f"Test report saved to: {output_file}")


if __name__ == "__main__":
    runner = TestRunner()
    
    # Example usage
    print("Running smoke tests...")
    smoke_results = runner.run_smoke_tests()
    create_test_report(smoke_results, "smoke-test-report.html")
    
    if smoke_results["success"]:
        print("Running full test suite...")
        full_results = runner.run_with_coverage()
        create_test_report(full_results, "full-test-report.html")