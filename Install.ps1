param(
    [Parameter(Mandatory=$true)][string]$GamePath,
    [Parameter(Mandatory=$true)][string]$ProfilePath,
    [ValidateSet('PRK_AOU_CYT','PRK_AOU_Slim_CNI','PRK_AOU_Slim_CNT')][string]$Layout='PRK_AOU_CYT',
    [string]$StateDirectory=(Join-Path $env:USERPROFILE '.prk-aou-mod'),
    [switch]$DryRun
)
$ErrorActionPreference='Stop'
$arguments=@((Join-Path $PSScriptRoot 'tools\install_gui.py'),'install','--game',$GamePath,'--profile',$ProfilePath,'--state',$StateDirectory,'--layout',$Layout)
if ($DryRun) { $arguments+='--dry-run' }
& python @arguments
if ($LASTEXITCODE -ne 0) { throw 'PRK AOU installation did not complete; inspect the reported error.' }
