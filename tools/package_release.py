"""Prepare a small Vita translation bundle; preview unless --write."""
import argparse
import sys

if __name__ == '__main__':
    selector = argparse.ArgumentParser(add_help=False)
    selector.add_argument('--format', choices=('pkg', 'cpk'), default='pkg')
    options, remaining = selector.parse_known_args()
    sys.argv = [sys.argv[0], *remaining]
    if options.format == 'cpk':
        from package_cpk_release import main
    else:
        from package_pkg_release import main
    main()
