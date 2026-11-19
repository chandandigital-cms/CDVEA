"""Copy the complete CDVEA bundle as one standalone skill, preserving internal paths."""
import argparse
from pathlib import Path
import shutil
import sys

def main():
    parser=argparse.ArgumentParser(description='Install CDVEA into an explicitly selected skills parent directory')
    parser.add_argument('--target',required=True,help='Parent skills directory, for example PROJECT/.agents/skills')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    dest=(Path(args.target).expanduser().resolve()/'cdvea')
    if dest==root or root in dest.parents or dest in root.parents:
        parser.error('Choose a destination outside this source bundle')
    if dest.exists():parser.error('Destination already exists; choose a new location or back up the existing installation')
    shutil.copytree(root,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc','node_modules','tests','TEST-RESULTS.json'))
    print(f'Installed CDVEA by Chandan Digital: {dest}')
    print('Reload the host skill list. The root cdvea skill routes to all bundled modes.')
    return 0
if __name__=='__main__':sys.exit(main())
