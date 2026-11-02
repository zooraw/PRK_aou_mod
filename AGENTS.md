# PRK AOU Mod

- Target only the separately selected Project Rubi-Ka client and its profile.
  Never deploy this package to regular AO or reuse retail renderer addresses.
- Keep real game/profile/state paths, credentials, account identifiers, screenshots,
  backups and logs outside Git. Check exact staged files, binary metadata and an
  intentionally public author identity before any publication.
- The installer copies Settings Root, HotKeys and Skills from the selected PRK
  client's Default GUI at deployment time. Do not restore retail settings overrides:
  the renderer binding contracts differ. Do not publish extracted vanilla assets.
- Daily/Pending Rewards, Research and Mechs exist in the inspected PRK default
  menus; do not remove them by assuming they are retail-only.
- Preserve installed renderer, browser shim, launcher and all account/auth files.
  Only the GUIName preference is owned; uninstall must retain unrelated settings.
- Optional armor controls belong to the separate armor installer. Remove its
  integration before removing this GUI when those files have been modified.
- No settings/skills source XML should be added merely to duplicate PRK Default;
  copy the local installed definitions and validate them during installation.
- Validate proportionately: XML parse, exact native-binding copy and deployed
  file hashes. Runtime visual testing must be described separately. The user
  waived equipped-armor testing for the new account.
