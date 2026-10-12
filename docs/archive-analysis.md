# Decrypted archive analysis — 0.1.2

Checked 2026-10-10 after the supplied matching local license enabled PFS decryption. The earlier PFS barrier described in `package-analysis.md` is resolved for this local working copy. No license value is recorded here.

## Verified archive inventory

`work/source/decrypted/cpk/Ange.cpk` has a valid `CPK ` signature. Its named TOC is a CRI `@UTF` table. `tools/cpk_extract.py` reads the CPK header and TOC, decodes UTF table storage flags, checks member paths, lists sizes and signatures in its default read-only mode, and can extract to a new directory. Compressed members are expanded with CRILAYLA and every extracted length is checked against `ExtractSize`.

- Named members: **4,486**.
- CRILAYLA compressed members: **2,927**.
- Stored member bytes: **877,242,747**.
- Expanded member bytes: **1,591,898,258**.
- Full local manifest: ignored `work/source/archive-manifest.json`.
- Readable text subset: ignored `work/source/archive/text/`.
- Complete extraction destination: ignored `work/source/archive/assets/`.
- `work/source/archive/full/` and `full_complete/` are interrupted partial attempts; do not use them as the corpus.

The largest text-related groups are **462 `.txt`**, **462 `.csv`**, and **100 `.json`** members. The JSON files are Live2D model descriptors, not assumed to be dialogue. Other members include 1,875 BTX texture files and compiled script/event assets. Counts are archive-member counts, not translation row counts.

## Scenario schema ready for translation

The scenario sources are paired under `data/_scr/`, for example `100111.txt` and `100111.csv`.

- `.txt`: UTF-16LE with BOM; CSV records. The verified first file contains 16 records with four fields: message ID, speaker, display text, voice ID.
- `.csv`: command stream; ASCII-compatible commands such as `ADV_MSG,1` refer to the matching text-table message ID. Character load/display commands provide additional visual context.
- Text uses runtime control markers including `#n`. Preserve these exactly in translations.
- UI `.inc` files observed under `data/_ui/` contain button constant definitions. These are game identifiers and must remain unchanged.

Each text file's schema and quoting must be validated before counting or exporting its rows. Do not combine TXT rows with their command references as duplicate dialogue. Do not count every binary Japanese-looking string as script. Preserve one source record per translation record and keep stable file/message IDs.

## Reproduction and validation

The default command was run and its sample member offsets, paths, sizes, and compression signatures inspected before extraction. A text subset was then extracted and inspected: UTF-16LE decoding and CSV parsing gave coherent dialogue/speaker records, confirming the CRILAYLA output. An optional C accelerator was compiled and its first decoded member compared against the Python decoder before use. All 4,486 members were extracted successfully, every size matched the manifest, and all text-subset files matched byte-for-byte between the Python and native decoders. Extraction writes new files only and refuses an existing extraction root. Input archives are opened read-only.

```powershell
python tools/cpk_extract.py work/source/decrypted/cpk/Ange.cpk
python tools/cpk_extract.py work/source/decrypted/cpk/Ange.cpk --manifest work/source/archive-manifest.json --extract work/source/archive/text --include '*.csv' --include '*.txt' --include '*.json' --include '*.inc'
python tools/cpk_extract.py work/source/decrypted/cpk/Ange.cpk --extract work/source/archive/assets
```

Format implementation references: the original author's [UTF parser](https://github.com/kamikat/cpktools/blob/master/cpk/utf.py) and [CRILAYLA decompressor](https://github.com/kamikat/cpktools/blob/master/cpk/crilayla.py). Our helper uses Python's standard library and does not require the old Python 2 code or third-party bitarray package.

For fast full-archive decompression, compile the optional accelerator using `gcc -O3 -shared -o tools/cpk_crilayla.dll tools/cpk_crilayla.c`, then run the helper with a 64-bit Python interpreter. The bundled interpreter is `C:\Users\Binh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. The system `C:\Python\python.exe` is 32-bit and uses the slower Python fallback. The generated DLL should remain ignored.

## Changelog

- 0.1.2 (2026-10-10): Parsed the decrypted CPK TOC, quantified members and compression, extracted readable scenario sources, identified message/command pairing and encoding, and added a reproducible extractor. No playable build or release.
