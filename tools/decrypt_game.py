"""Preview PCSG00597 PC decryption; --run needs a matching local license file.

Uses the verified local Vita3K distribution and its native F00D implementation.
License values are never printed. Game input and existing output are not overwritten.
"""
import argparse
import base64
import json
import shutil
import subprocess
import zlib
from pathlib import Path

from pkg_probe import probe

ROOT = Path(__file__).resolve().parents[1]
CONTENT_ID = "JP0700-PCSG00597_00-CROSSANGEGAME000"
VENDOR = ROOT / "tools/pkg_vendor/vita3k-20261010"
DICTIONARY = zlib.decompress(base64.b64decode(
    b"eNpjYBgFo2AU0AsYAIElGt8MRJiDCAsw3xhEmIAIU4N4AwNdRxcXZ3+/EJCAkW6Ac7C7ARwYgviuQAaIdoPSzlDaBUo7QmknIM3ACIZM78+u7kx3VWYEAGJ9HV0="))


def load_license(path):
    data = path.read_bytes()
    if len(data) in (512, 1024):
        rif = data
        compressor = zlib.compressobj(level=9, wbits=10, memLevel=8, zdict=DICTIONARY)
        compressed = compressor.compress(rif) + compressor.flush()
        compressed += b"\0" * (-len(compressed) % 3)
        zrif = base64.b64encode(compressed).decode("ascii")
    else:
        if len(data) > 8192:
            raise ValueError("License input is too large; supply one RIF or zRIF file.")
        fields = data.decode("utf-8-sig").split()
        if len(fields) == 2 and fields[0] == CONTENT_ID:
            fields = fields[1:]
        if len(fields) != 1:
            raise ValueError("Expected one zRIF string in the text file.")
        zrif = fields[0]
        encoded = base64.b64decode(zrif, validate=True)
        decoder = zlib.decompressobj(wbits=15, zdict=DICTIONARY)
        rif = decoder.decompress(encoded, 1025)
        if not decoder.eof or len(rif) not in (512, 1024):
            raise ValueError("Expected a complete 512/1024-byte decompressed license.")
    content = rif[0x10:0x40].rstrip(b"\0").decode("ascii")
    if content != CONTENT_ID:
        raise ValueError("License content ID does not match PCSG00597.")
    if not any(rif[0x50:0x60]):
        raise ValueError("License has an empty key; it cannot decrypt the game.")
    return zrif


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path)
    parser.add_argument("--license", type=Path, help="Local RIF/work.bin or text containing one zRIF.")
    parser.add_argument("--run", action="store_true", help="Decrypt after reviewing a successful preview.")
    args = parser.parse_args()
    packages = list(ROOT.glob("*.pkg"))
    package = args.package.resolve() if args.package else (packages[0] if len(packages) == 1 else None)
    if package is None:
        parser.error("Specify --package; exactly one root PKG was not found.")
    metadata = probe(package)
    if metadata["content_id"] != CONTENT_ID:
        parser.error("Package content ID does not match this project.")
    executable = VENDOR / "Vita3K.exe"
    portable = VENDOR / "portable"
    installed = portable / "fs/ux0/app/PCSG00597"
    destination = ROOT / "work/source/decrypted"
    zrif = None
    error = None
    if args.license is None:
        error = "Matching local license file is missing; use --license PATH."
    else:
        try:
            zrif = load_license(args.license)
        except (OSError, ValueError, UnicodeError, zlib.error) as problem:
            error = str(problem)
    if not executable.is_file():
        error = "Verified Vita3K distribution is missing."
    if installed.exists() or installed.with_name("PCSG00597_dec").exists() or destination.exists():
        error = "An output directory already exists; inspect it before any new run."
    print(json.dumps({"package": str(package), "content_id": CONTENT_ID,
                      "decryptor": str(executable), "native_f00d": True,
                      "license_present_and_matches": zrif is not None,
                      "license_value": "never displayed", "isolated_install": str(installed),
                      "destination": str(destination), "run": args.run,
                      "ready": error is None, "blocker": error}, indent=2))
    if not args.run:
        return
    if error is not None:
        parser.error(error)
    # Upstream detects this local directory before loading user emulator settings.
    portable.mkdir(parents=True, exist_ok=True)
    if (portable / "config.yml").exists():
        config = (portable / "config.yml").read_text(encoding="utf-8-sig")
        if 'pref-path: ""' not in config:
            parser.error("Portable settings have a custom filesystem path; inspect before running.")
    log_dir = ROOT / "work/source/decryption-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "vita3k-install.log"
    with log_path.open("xb") as log:
        result = subprocess.run([str(executable), "--pkg", str(package), "--zrif", zrif],
                                cwd=str(VENDOR), stdout=log, stderr=subprocess.STDOUT,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    archive = installed / "cpk/Ange.cpk"
    signature = b""
    if archive.is_file():
        with archive.open("rb") as stream:
            signature = stream.read(4)
    if result.returncode != 0 or signature != b"CPK ":
        raise SystemExit("Decryption did not produce a readable CPK. Inspect the ignored local log; no source copy exported.")
    # Preserve only verified output. Existing directories are never replaced.
    shutil.copytree(installed, destination)
    print(json.dumps({"status": "decrypted_cpk_signature_verified",
                      "output": str(destination), "cpk_bytes": archive.stat().st_size,
                      "note": "CPK table/script format still need inspection before text counting."}, indent=2))


if __name__ == "__main__":
    main()
