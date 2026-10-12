# Release packaging

Release v0.1.13 packages the already built game files; packaging does not create another game build. A new game binary requires a new version. Follow the public [Retro Trans release standard](https://github.com/retro-trans/retro-trans-tools/blob/main/docs/RELEASE_STANDARD.md).

The package uses manifest schema 2 with one explicit two-file solution: original `cpk/Ange.cpk` and `sce_sys/param.sfo`. Component identities and output names are stable. Automatic mode produces a new flat folder with both patched files; installation places them in their proper app directories. The credits page and font license are separate extras rather than original game files or synthetic source components.

Use the sibling `../retro-trans-tools` checkout, commit the reviewed Cross Ange source snapshot, then preview:

```text
python tools/package_release.py --build 0.1.13
python tools/package_release.py --build 0.1.13 --write
```

The packager uses Retro Trans's release builder to hash originals and targets, generate xdelta patches without private filename headers, decode both patches, compare complete targets and recheck unchanged inputs. The manifest records the actual source commit. It also verifies the extras ZIP after writing. Private source paths/configuration and engine cache remain under `work/source/release-packaging/`; public artifacts go to ignored `work/output/releases/v0.1.12/`.

Required protocol assets are `BUILD-MANIFEST.json`, both xdelta patches, `SHA256SUMS.txt` and `VALIDATION.json`. Extras have their own ZIP checksum. Publish only this allowlisted package after checking uploaded sizes and hashes. Game builds, installed apps, packages, licenses and Japanese working files must not be uploaded. Publishing requires an explicit user request.

Version 0.1.13 additionally creates `VITA-PKG.json`, `Cross-Ange-English-0.1.13-Vita-PKG-patches.zip` and `VITA-PKG-SHA256SUMS.txt`. The generic Retro Trans 0.5.8 profile describes the exact original PKG, all 46 decrypted originals, two translation patches and two generated extras. The ZIP contains only the profile, deltas, credits and font license. The app supplies the encryption code and the user supplies a matching license. Existing standard component assets remain compatible with older Automatic/Apply xdelta clients. See the sibling project's `docs/VITA_PKG.md` for the reusable profile contract.

The repository remains private. Creating or updating a release here does not authorize publishing a Retro Trans app release or making this repository public.
