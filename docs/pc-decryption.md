# PC decryption record — 0.1.2

Checked 2026-10-10. **Decryption succeeded using the matching user-supplied `incoming/work.bin`.** This is an extraction/translation milestone, not a playable build.

## Installed and checked

- Official [psvpfstools v2.0 Windows release](https://github.com/motoharu-gosuto/psvpfstools/releases/tag/v2.0), in ignored `tools/pkg_vendor/psvpfstools-v2.0-win64/`. Its executable runs and lists its decryption options. This published binary supports the older online F00D route; it does not expose the cache option documented by newer source.
- Official [Vita3K Windows distribution](https://github.com/Vita3K/Vita3K/releases/tag/continuous), in ignored `tools/pkg_vendor/vita3k-20261010/`. Version check returned `Vita3K v0.2.1 4154-b75d5e62`. Help confirms `--pkg` and `--zrif`; portable mode was enabled and checked locally.
- `tools/decrypt_game.py` previews a decryption plan by default. It uses Vita3K's native F00D implementation, so no online key-conversion service is configured. This behavior is verified in the matching [Vita3K package installer source](https://github.com/Vita3K/Vita3K/blob/b75d5e62/vita3k/packages/src/pkg.cpp).

The read-only preview passed the matching content-ID and nonempty-key checks. The subsequent Vita3K install succeeded; the archive begins with `CPK ` and all 4,486 members were later extracted and size-validated. The decrypted app is in ignored `work/source/decrypted/`; its manual pages are readable PNGs.

## License history

At milestone 0.1.1 no matching license was available. Standard Vita3K license locations contained no matching PCSG00597 file; the supplied game ZIP contained only the package.

The first user-provided license belonged to `JP0700-PCSG00264_00-SRWZ3OF1DLGPKG00` and was rejected before execution. The user later obtained Cross Ange's matching license, placed it at `incoming/work.bin`, and authorized continuation. It successfully decrypted `JP0700-PCSG00597_00-CROSSANGEGAME000`. No key was printed in chat or sent to a key-conversion service.

Supply the path to a matching NoNpDrm `work.bin`/`.rif`, or a local text file holding its zRIF. The expected content ID is `JP0700-PCSG00597_00-CROSSANGEGAME000`. File contents do not need to be pasted into chat. Keep license files under ignored `incoming/` or `work/source/`. The [official Vita3K quickstart](https://vita3k.org/quickstart.html) documents the game-specific NoNpDrm license and its `work.bin` use.

## Reproduction

```powershell
# Read-only preview: rejects a different content ID or an empty key.
python tools/decrypt_game.py --license incoming/work.bin

# After inspecting a successful preview, run the requested decryption.
python tools/decrypt_game.py --license incoming/work.bin --run
```

The original package is read-only input. Vita3K installs into its isolated project-local portable filesystem. The helper refuses pre-existing game output and preserves process output in ignored `work/source/decryption-logs/`. License values are not printed by the helper or sent to an online service. The native tool may include source metadata or cryptographic diagnostics in its ignored logs.

The helper copies the app only after a successful exit and CPK signature check. Those checks and subsequent table/member/script validation passed in 0.1.2. Existing output is rejected on a rerun; use the current decrypted copy. See [archive analysis](archive-analysis.md) and [text inventory](text-inventory.md).

## Provenance

Downloaded archives are ignored local dependencies in `tools/pkg_downloads/`.

| Archive | SHA-256 | Check |
|---|---|---|
| `psvpfstools-v2.0-win64.zip` | `441cac58455caae9187affc390595c6c74446351de82f426fb2afc040f4618bf` | Downloaded from author's release; locally hashed |
| `vita3k-windows-20261010.zip` | `1bb36321376b5ce34d8ede5fc5a759b547ff39269316b02f44ba11cedc06b0bc` | Matches SHA-256 published in GitHub release API |

The license encoder uses the public zRIF dictionary and compression format documented by [pkg2zip's rif2zrif.py](https://github.com/mmozeiko/pkg2zip/blob/master/rif2zrif.py). It validates the embedded content ID before invoking the installer. Matching that identifier alone does not prove a license key is valid; successful decryption must establish that.
