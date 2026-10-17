"""Fail-closed publication context for Cloudflare's Linux Workers Builds."""
import os
from pathlib import Path


def command_from_argv(argv):
    """Read the literal command after a real Wrangler Node entrypoint."""
    if not argv or Path(argv[0]).name not in ('node', 'nodejs'):
        return None
    for i, arg in enumerate(argv[1:], 1):
        script=arg.replace('\\', '/')
        if '/wrangler/' in script and script.endswith(('/bin/wrangler.js','/wrangler-dist/cli.js')):
            command=argv[i+1:]
            # Unknown/global-option forms stay closed rather than guessing.
            if command and command[0] in ('deploy','preview','dev','types'):
                return command[0]
            if command[:2]==['versions','upload']:
                return 'versions upload'
            return None
    return None


def detect_wrangler_command(proc_root=Path('/proc'), start_pid=None):
    """Observe the closest actual Wrangler ancestor, never a user-supplied flag.

    Cloudflare Workers Builds uses Linux. Outside Linux or without readable
    process metadata, return unknown and leave publication disabled.
    """
    pid=os.getppid() if start_pid is None else start_pid
    seen=set()
    for _ in range(16):
        if pid<=1 or pid in seen:
            return None
        seen.add(pid)
        try:
            argv=[x.decode('utf-8') for x in (proc_root/str(pid)/'cmdline').read_bytes().split(b'\0') if x]
            # Stop at the closest Wrangler, including an unrecognised form.
            if any('/wrangler/' in arg.replace('\\','/') and arg.endswith(('/bin/wrangler.js','/wrangler-dist/cli.js')) for arg in argv[1:]):
                return command_from_argv(argv)
            status=(proc_root/str(pid)/'status').read_text()
            pid=int(next(line.split(':',1)[1] for line in status.splitlines() if line.startswith('PPid:')))
        except (OSError,UnicodeError,StopIteration,ValueError):
            return None
    return None


def indexing_allowed(approved, environ, actual_command):
    if approved is not True:
        return False
    claimed_main=(environ.get('WORKERS_CI')=='1' and environ.get('WORKERS_CI_BRANCH')=='main'
                  and environ.get('WRANGLER_COMMAND')=='deploy')
    if claimed_main and actual_command is None:
        raise ValueError('Cannot verify actual Wrangler command on main; publication stopped')
    return claimed_main and actual_command=='deploy'
