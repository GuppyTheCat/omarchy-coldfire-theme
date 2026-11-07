import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "contrast-check"

PASSING_PALETTE = {
    "background": "#0b0f1c",
    "lighter_background": "#151b2e",
    "selection": "#263355",
    "muted": "#5e6b98",
    "foreground": "#d6deef",
    "dark_foreground": "#949db9",
    "light_foreground": "#e6ecf7",
    "bright_foreground": "#f4f7ff",
    "accent": "#ff8a4c",
    "red": "#ff6b6b",
    "orange": "#ff8a4c",
    "yellow": "#f5c26b",
    "green": "#7dd3a0",
    "cyan": "#6cc8f5",
    "blue": "#5b9cff",
    "magenta": "#d686d9",
    "brown": "#b5835a",
}


def run_check(palette):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "colors.toml"
        path.write_text("".join(f'{key} = "{value}"\n' for key, value in palette.items()))
        return subprocess.run([SCRIPT, path], capture_output=True, text=True)


def line_for(output, foreground, background):
    for line in output.splitlines():
        words = line.split()
        if words[1:3] == [foreground, background]:
            return line
    raise AssertionError(f"no line for {foreground} on {background} in:\n{output}")


class ContrastCheckTest(unittest.TestCase):
    def test_readable_palette_exits_zero(self):
        result = run_check(PASSING_PALETTE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("FAIL", result.stdout)

    def test_dim_muted_fails_and_exits_one(self):
        result = run_check({**PASSING_PALETTE, "muted": "#1a1d2a"})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(line_for(result.stdout, "muted", "background").startswith("FAIL"))

    def test_white_on_black_reports_maximum_ratio(self):
        result = run_check({**PASSING_PALETTE, "foreground": "#ffffff", "background": "#000000"})
        self.assertIn("21.00", line_for(result.stdout, "foreground", "background"))

    def test_missing_file_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [SCRIPT, Path(tmp) / "absent.toml"], capture_output=True, text=True
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
