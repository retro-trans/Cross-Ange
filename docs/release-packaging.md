# Whole-PKG release packaging

Updating v0.1.13's distribution format does not change its game files, footer or
credits version. A new game binary requires a new version. The current player
route is whole-PKG xdelta; the previous CPK/component route is retired.

The local Retro Trans Tools 0.5.12 source supplies the generic
`retro-trans-vita-pkg-xdelta-v1` contract. Use `tools/package_release.py` to
preview, then add `--write` to generate a new verified asset folder:

```text
python tools/package_release.py --build 0.1.13 --package Original.pkg --translated-pkg English.pkg
```

The original and translated packages must match the publisher's recorded native
verification. Packaging does not read a license. It creates or reuses a whole-PKG
delta, decodes it completely, checks the output and unchanged inputs, verifies
the ZIP's exact inventory and writes checksums. `--delta Existing-PKG.xdelta`
reuses a local patch only after another complete round trip. Preview does not
write output. Existing release folders are preserved.

The release allowlist is:

- `VITA-PKG-XDELTA.json`: exact original, output and delta identities;
- `Cross-Ange-English-0.1.13-Vita-PKG-xdelta.zip`: that profile and one delta;
- `VALIDATION.json`: native-output provenance and local packaging verification;
- `AUTOMATIC-VALIDATION.json`: private-release download and Automatic checks;
- `SHA256SUMS.txt`: checksums of those downloads.

The flat ZIP contains no extra files. The current delta is about 945 MB, almost
the output package's size; release notes must make this size clear. Full `.pkg`
files, licenses, executables, extracted artwork and Japanese working scripts
remain local. No CPK deltas, old per-file profiles, component manifest or extras
ZIP should be included in the current release.

Upload and verify the new ZIP/profile before removing retired assets. Test a
fresh download through the local frozen 0.5.12 app with no local patch argument,
then test its Automatic UI worker. Compare complete source/output identities.
Preserve historical validation records in Git; mark them as superseded rather
than rewriting their original results. The game repository/release stays private.

Publication requires an explicit user request. Updating this game release does
not authorize a Retro Trans Tools release or source push. Keep the tools 0.5.12
build local until its own publication is requested.
