param(
    [ValidateSet('auto','claude','codex','both','none')][string]$Hosts = 'auto',
    [string]$RuntimeDir,
    [switch]$Check
)
$ErrorActionPreference = 'Stop'
$setupScript = Join-Path $PSScriptRoot 'setup.py'
$setupArgs = @($setupScript, '--hosts', $Hosts)
if ($RuntimeDir) { $setupArgs += @('--runtime-dir', $RuntimeDir) }
if ($Check) { $setupArgs += '--check' }
if (Get-Command python -ErrorAction SilentlyContinue) {
    & python @setupArgs
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 @setupArgs
} else {
    throw 'Install Python 3.10 or newer, reopen PowerShell, then run setup.ps1 again.'
}
exit $LASTEXITCODE
