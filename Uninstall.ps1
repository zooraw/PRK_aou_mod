param([string]$StateDirectory=(Join-Path $env:USERPROFILE '.prk-aou-mod'))
$ErrorActionPreference='Stop'
& python (Join-Path $PSScriptRoot 'tools\install_gui.py') uninstall --state $StateDirectory
if ($LASTEXITCODE -ne 0) { throw 'PRK AOU removal refused. Preserve the changed files and inspect the error.' }
