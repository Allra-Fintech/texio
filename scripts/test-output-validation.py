#!/usr/bin/env python3
"""Reject plausible but incorrect captured output without changing user files."""
import argparse
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from unittest.mock import patch


def main():
    """Inject four output faults and require the intended validation failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--texio', type=Path, required=True)
    args = parser.parse_args()
    scripts = Path(__file__).resolve().parent
    original_run = subprocess.run
    for mode in ('headings', 'preview', 'diff-extra', 'diff-stderr'):
        def faulty(command, *positional, fault_mode=mode, **keywords):
            """Alter captured output for this fault while executing the real command."""
            result = original_run(command, *positional, **keywords)
            if fault_mode == 'headings' and command[1] == 'headings':
                result.stdout = b'[]'
            elif fault_mode == 'preview' and '--dry-run' in command:
                result.stdout = b''
            elif fault_mode.startswith('diff-') and command[0] == 'git':
                if fault_mode == 'diff-extra':
                    result.stdout += '+unexpected change\n'
                else:
                    result.stderr = 'unexpected warning\n'
            return result
        with tempfile.TemporaryDirectory(prefix='texio-output-fault-') as temporary:
            recorder = mode.startswith('diff-')
            script = scripts / ('record-section-demo.py' if recorder else 'check-practitioner-kit.py')
            argv = [str(script), '--texio', str(args.texio.resolve())]
            output = Path(temporary) / 'demo'
            if recorder:
                argv += ['--output-dir', str(output)]
            expected = {'headings': 'unexpected headings', 'preview': 'preview missing replacement',
                        'diff-extra': 'unexpected diff output', 'diff-stderr': 'unexpected diff output'}[mode]
            with patch.object(sys, 'argv', argv), patch.object(subprocess, 'run', faulty):
                try:
                    runpy.run_path(str(script), run_name='__main__')
                except ValueError as error:
                    if str(error) != expected:
                        raise
                else:
                    raise ValueError('accepted bad output: ' + mode)
            if output.exists():
                raise ValueError('wrote artifacts after bad output')
            print('Rejected bad output:', mode)


if __name__ == '__main__':
    main()
