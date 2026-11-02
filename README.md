# PRK AOU Mod

A separate Project Rubi-Ka edition of AOU Mod, based on the maintained
[zooraw/aou_mod](https://github.com/zooraw/aou_mod) fork and
[dracul89/aou_mod](https://github.com/dracul89/aou_mod). Original AOU design:
Scene; upstream version 1.2.5. Existing GPL notices and credits are retained.

This edition targets the installed PRK **00.7.2_EP1** client. It uses its own
`PRK_AOU_CYT`, `PRK_AOU_Slim_CNI` and `PRK_AOU_Slim_CNT` layout names and affects
only the explicitly selected PRK client/profile. It does not alter regular AO,
PRK's Vulkan renderer, browser shim, launcher, authentication or game database.

## Install

Requirements: Python 3.13 or 3.14, PRK with the supported version, and the game
closed normally. Keep this source in a stable directory and run:

```powershell
.\Install.ps1 -GamePath 'C:\Games\Project Rubi-Ka\client' -ProfilePath 'C:\LocalPrefs\PRK\client'
```

`GamePath` is the `client` subdirectory next to the PRK launcher.
`ProfilePath` is the AppData profile containing `Prefs`, `Gui` and `scripts`.
Find it under `%LOCALAPPDATA%\Funcom\Anarchy Online\<installation>\client`.
These are generic examples; keep real paths and account settings local.

The installer activates `PRK_AOU_CYT` by changing only the profile's `GUIName`.
Choose another layout with `-Layout PRK_AOU_Slim_CNI` or `PRK_AOU_Slim_CNT`.
`-DryRun` prepares and validates a plan without writes and can run while the
client is open. State/backups default to `%USERPROFILE%\.prk-aou-mod`; override
with `-StateDirectory` outside this source tree if needed.

Start PRK normally after installation. The AOU button opens the familiar menu.
The legacy `/script aou_gui_default` and `/script aou_gui_slim*` commands select
these PRK layouts; `/script prk_aou_default` explicitly selects the default PRK
AOU layout. `/script ao_original` selects the game's Default GUI.

## Compatibility choices

Settings, fixed keys and Skills definitions are copied **from the installed
PRK Default GUI at installation time**, not from retail AO. This avoids obsolete
checkbox/radio bindings and keeps the client's exact category names and values.
No extracted vanilla definitions are shipped in this source repository.

Daily/Pending Rewards, Research and Mechs remain available because those names
are present in the inspected PRK default menus. Their service/content behavior
is owned by PRK; menu presence alone does not establish service availability.
AOU help/voice filename fixes and the upstream artwork/menu layouts are retained.
The optional Basic-voice reconstruction helper remains in `tools`; use it only
with the chosen PRK GamePath if those local sounds are needed.

Armor controls are not built into this base package. The separate PRK-compatible
armor installer can add its optional controls after this GUI is installed.

## Remove

Close PRK normally, remove optional armor integration first, then run:

```powershell
.\Uninstall.ps1
```

Use the same `-StateDirectory` if you selected one. The installer verifies owned
file hashes before removal, restores overwritten files, and restores GUIName
only if it still selects this layout. Unrelated settings changed while playing
are preserved. Changed files are not overwritten on uninstall/reinstall; inspect
that conflict rather than force a stale backup over user work.

## Verification and limits

The prepared package and actual installation passed these focused checks:

- 710 deployed file hashes matched the prepared plan.
- All nine locally copied native definitions (three layouts each containing
  Settings Root, HotKeys and Skills) matched PRK Default byte-for-byte.
- All 153 native settings bindings/types/values/categories were preserved.
- GUIName activation/restoration retained unrelated preferences changed during
  play; duplicate GUIName values were rejected.
- The 132 distributed source XML files parsed strictly. Validation of the 142
  deployment XML definitions also accommodates the client's raw HTML attribute
  dialect in its native Skills view without changing the deployed bytes.

These are source/deployment checks, not an observed in-game GUI run. Equipped-
armor appearance testing was waived for the new account. Existing PRK browser/
renderer modifications were preserved; no launcher or authentication was automated.

No account data, private paths, deployment logs, original sound files, database
records or backups are part of this repository. Read [AGENTS.md](AGENTS.md)
before contributing. The original AOU GPL license applies.
