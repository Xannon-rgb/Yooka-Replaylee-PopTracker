# Yooka-Replaylee-PopTracker
This is a poptracker for Yooka Replaylee archipelago.
This is still being worked on, if you find errors please let me know via Discord.

## Install the 2.70.0 release

1. Use **PopTracker 0.35.4 or later**.
2. Open the [latest release](https://github.com/Xannon-rgb/Yooka-Replaylee-PopTracker/releases/latest).
3. Download **Yooka-Replaylee_PopTracker_v2.70.0.zip** from Assets.
4. Drag the ZIP into PopTracker, or copy it into your PopTracker packs folder without extracting it.
5. Load the pack and select HD, Full HD, 1440p, 4K, or Horizontal/Widescreen.

Use the named tracker ZIP. GitHub's **Source code** downloads are repository maintenance snapshots, not installable packs. The archived original ZIP is retained only for recovery.

Connect using PopTracker's Archipelago controls with your server, slot name, and room password if required.

## Automatic pack-update feed

The pack points to [versions.json](https://raw.githubusercontent.com/Xannon-rgb/Yooka-Replaylee-PopTracker/main/versions.json). GitHub Actions updates it after releases are published or edited, with hourly checks for late attachments. Each entry contains the internal pack version, download URL, and verified SHA-256 checksum.

PopTracker uses this feed for pack updates. Older packs without the update URL need a one-time manual installation of the current release.

## Publishing future versions

- Change the pack files, then increase `package_version` inside `manifest.json`, for example to `2.71.0`. Update the displayed version labels too.
- Preserve `package_uid` and `versions_url`.
- ZIP the pack with `manifest.json` at the root.
- Attach one ZIP named `Yooka-Replaylee_PopTracker_v2.71.0.zip` to the matching GitHub release, then publish it.
- Confirm that **Update PopTracker release feed** succeeds in Actions. Drafts and prereleases are excluded.

Renaming a ZIP alone does not change its internal version. This repository distributes complete packs through Releases; editing maintenance files does not rebuild the gameplay pack.

## 2.70.0 validation

The ZIP integrity, 18 JSON files, four Lua scripts' syntax, referenced image/layout files, and update-feed replacement/checksum handling have been checked. The launch correction changes only version metadata inside the pack.

A live PopTracker session and real Archipelago connection still need a gameplay smoke test.
