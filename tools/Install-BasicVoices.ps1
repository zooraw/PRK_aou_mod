param(
    [Parameter(Mandatory = $true)]
    [string]$GamePath
)

$ErrorActionPreference = 'Stop'
$game = (Resolve-Path -LiteralPath $GamePath).Path
$sound = Join-Path $game 'cd_image\sound'
$player = Join-Path $sound 'sfx\player'
if (-not (Test-Path -LiteralPath $player -PathType Container)) {
    throw "AO sound directory not found: $player"
}
$targetRoot = Join-Path $player 'AOU_mod\Basic'
$menu = Join-Path $PSScriptRoot '..\scripts\AOU_mod\Voicepack\Basic.htm'
$entries = [regex]::Matches([IO.File]::ReadAllText($menu), '<a href="chatcmd:///voice AOU_mod\\Basic\\([^"<>]+)">([^<]+)</a>')
if ($entries.Count -eq 0) { throw 'No Basic voice menu entries found' }
$sourceFiles = @(Get-ChildItem -LiteralPath $sound -Filter '*.wav' -Recurse -File |
    Where-Object { -not $_.FullName.StartsWith($targetRoot + '\', [StringComparison]::OrdinalIgnoreCase) })
$utf8 = [Text.UTF8Encoding]::new($false)
$plan = @()

foreach ($entry in $entries) {
    $name = $entry.Groups[1].Value
    if ($name -notmatch '^[A-Za-z0-9_]+$') { throw "Unexpected voice name: $name" }
    $filename = $name + '_01.wav'
    if ($name -eq 'yottos_song1') { $filename = 'yottos_song_01.wav' }
    if ($name -eq 'yottos_song6') { $filename = 'yottos_song_06.wav' }
    $candidates = @($sourceFiles | Where-Object { $_.Name -eq $filename })
    if ($name -eq 'munk') {
        $candidates = @(Get-Item -LiteralPath (Join-Path $sound 'music\env\trade\night\munk_01.wav'))
    }
    if ($candidates.Count -eq 0) { throw "Shipped sound not found: $filename" }
    $hashes = @($candidates | ForEach-Object { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash } | Select-Object -Unique)
    if ($hashes.Count -ne 1) { throw "Ambiguous shipped sound: $filename" }
    $bytes = [IO.File]::ReadAllBytes($candidates[0].FullName)
    if ($bytes.Length -lt 12 -or [Text.Encoding]::ASCII.GetString($bytes, 0, 4) -ne 'RIFF' -or [Text.Encoding]::ASCII.GetString($bytes, 8, 4) -ne 'WAVE') {
        throw "Invalid WAV header: $filename"
    }
    $caption = [Net.WebUtility]::HtmlDecode($entry.Groups[2].Value)
    $plan += [pscustomobject]@{ Source = $candidates[0].FullName; Target = Join-Path $targetRoot ($name + '_01.wav'); Bytes = $null; Hash = $hashes[0] }
    $plan += [pscustomobject]@{ Source = $null; Target = Join-Path $targetRoot ($name + '_01.txt'); Bytes = $utf8.GetBytes($caption); Hash = $null }
}

# Complete conflict checks before creating or replacing files.
foreach ($item in $plan) {
    if (Test-Path -LiteralPath $item.Target) {
        if ($null -ne $item.Source) {
            $same = (Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash -eq $item.Hash
        } else {
            $same = [Convert]::ToBase64String([IO.File]::ReadAllBytes($item.Target)) -eq [Convert]::ToBase64String($item.Bytes)
        }
        if (-not $same) { throw "Existing differing file: $($item.Target)" }
    }
}
New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
foreach ($item in $plan) {
    if (-not (Test-Path -LiteralPath $item.Target)) {
        if ($null -ne $item.Source) { Copy-Item -LiteralPath $item.Source -Destination $item.Target }
        else { [IO.File]::WriteAllBytes($item.Target, $item.Bytes) }
    }
    if ($null -ne $item.Source -and (Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash -ne $item.Hash) {
        throw "Copied sound failed verification: $($item.Target)"
    }
    if ($null -eq $item.Source -and [Convert]::ToBase64String([IO.File]::ReadAllBytes($item.Target)) -ne [Convert]::ToBase64String($item.Bytes)) {
        throw "Caption failed verification: $($item.Target)"
    }
}
Write-Output "Verified $($entries.Count) Basic voice WAV/caption pairs in $targetRoot"
