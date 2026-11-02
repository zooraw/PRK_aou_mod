# Install the optional voice packs

AO resolves `/voice` paths relative to:

```text
<AO game folder>\cd_image\sound\sfx\player\
```

Each sound requires a matching `name_01.wav` and `name_01.txt`. Install the packs
in the **game installation**, not the AppData GUI directory. For example:

```text
C:\Games\Project Rubi-Ka\client\cd_image\sound\sfx\player\AOU_mod\Basic\
C:\Games\Project Rubi-Ka\client\cd_image\sound\sfx\player\AOU_mod\LineOfFire\
```

## Ariens' basic sounds

The 57 entries in the Basic menu can be prepared from the sounds already shipped
with AO. From the extracted repository folder, run in PowerShell:

```powershell
.\tools\Install-BasicVoices.ps1 -GamePath 'C:\Games\Project Rubi-Ka\client'
```

Supply your actual AO installation path. The script copies the matching shipped
sounds into `AOU_mod\Basic` and creates captions from this mod's menu labels.
This reconstructs the menu's required files; it is not a download of an original
Ariens audio archive. Original game sounds are preserved, identical destination
files are reused, and conflicting destination files cause an error before writes.

Two Yuttos entries use shipped `yottos_song_01.wav` and `yottos_song_06.wav`.
The ambiguous `munk` basename uses AO's Trade/night chanting recording.

## Windguaerd's Line of Fire v4.0

1. Download **Line of Fire v4.0** from
   [AO-Universe's voice packs page](https://www.ao-universe.com/multimedia/downloads/voice-packs).
2. Extract its `Voices` directory into a temporary folder. The download is a
   Clickteam installer; [cicdec](https://github.com/Bioruebe/cicdec) can extract its
   contents without running the installer. With cicdec's extracted executable:

   ```powershell
   .\cicdec.exe .\lof_voicepack_v4.0.exe .\lof-extracted
   ```

3. Copy the **contents** of `lof-extracted\Voices` (153 WAV/text pairs) into:

   ```text
   <AO game folder>\cd_image\sound\sfx\player\AOU_mod\LineOfFire\
   ```

4. Keep this fork's `lof_list.html` and `lof_macros.html` installed as described in
   the README. The old installer includes older menu files; do not replace the
   fork's menus with those files.

The v4.0 download used for testing had SHA-256:

```text
0569B40E72D9506DF47D26C9843390983250CF40EB0DF9A9FBCCCF25A83950D0
```

The two repaired menu filenames are `target_spotted` and `scratch_another_one`;
the original audio files do not have a `male_` prefix.

## Use and verification

Before testing, open **F10 → Audio**:

1. Enable **Sound On/Off** and set **Master Volume** above zero.
2. Enable **Voices On/Off** and set **Voices volume** above zero.
3. Under **Hear voices from**, enable **Vicinity** for the test below. Enable
   **Team channel**, **Guild channel**, or **Known friends** as needed for the
   channels you use.

Captions can appear even when voice playback is disabled or its channel is not
allowed. Earlier retail testing confirmed both sample clips after enabling the
voice settings; this does not establish PRK playback. If captions appear without sound, check these settings first,
then check AO's volume in the Windows Volume Mixer.

Open the AOU menu and select **Ariens VoicePack** or **WGs VoicePack**.

To test manually, press **Enter**, type one command, and press **Enter** again.
Run each line separately and wait a few seconds between clips. These commands
select Vicinity and can broadcast audio and captions to nearby players:

```text
/ch Vicinity
/voice AOU_mod\Basic\walkie
/voice AOU_mod\LineOfFire\access_granted
```

Expect the captions **Walkie-talkie** and **Access granted**, with their recorded
sounds. Return to your usual chat channel afterward. `/say Hello!` sends text to
nearby players; it does not speak the text aloud. Voice packs play prerecorded
clips rather than converting typed messages to speech.

The installed packs were checked for matching audio and captions for all 208
distinct menu commands. One sample from each pack played through Windows audio.
In-game `/voice` tests for `Basic\walkie` and `LineOfFire\access_granted`
displayed both expected captions with no missing-file errors. The user confirmed
hearing both clips in AO. Other-player reception has not been confirmed.
Other players need the same custom sound files to hear custom clips.

This guide covers the **Ariens VoicePack** and **WGs VoicePack** menus.
The separate **AriensGUI** menu opens a tools and shortcuts window using
`/showfile scripts\AOU_mod\AriensGUI\ArienskyPanelAOU.htm`; `/APanel` opens the
same window. It does not require a voice pack.

References: [AO-Universe voice commands](https://www.ao-universe.com/guides/notum-wars/gameplay-guides-4/voice-commands)
and [Ariensky's sound-effects guide](https://www.ao-universe.com/guides/classic-ao/gameplay-guides-6/how-to-play-soundeffects).
