#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil
import json

def get_platform_specific_name():
    """Get platform-specific executable name"""
    system = platform.system().lower()
    if system == 'windows':
        return 'rlgen.exe'
    return 'rlgen'

def check_swipl():
    """Check if SWI-Prolog is installed"""
    try:
        subprocess.run(['swipl', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def copy_required_files(project_root, dist_dir):
    """Copy all required files to the distribution directory"""
    # Create necessary directories
    scripts_dir = os.path.join(dist_dir, 'scripts')
    qe_dir = os.path.join(scripts_dir, 'QE')
    examples_dir = os.path.join(dist_dir, 'examples')
    
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(qe_dir, exist_ok=True)
    os.makedirs(examples_dir, exist_ok=True)
    
    # Copy config.json
    shutil.copy2(
        os.path.join(project_root, 'scripts', 'config.json'),
        os.path.join(scripts_dir, 'config.json')
    )
    
    # Copy DT-Golog.pl
    shutil.copy2(
        os.path.join(project_root, 'scripts', 'QE', 'DT-Golog.pl'),
        os.path.join(qe_dir, 'DT-Golog.pl')
    )
    
    # Copy example files if they exist
    examples_src = os.path.join(project_root, 'examples')
    if os.path.exists(examples_src):
        for root, dirs, files in os.walk(examples_src):
            for file in files:
                if file.endswith('.pl'):
                    rel_path = os.path.relpath(root, examples_src)
                    dst_dir = os.path.join(examples_dir, rel_path)
                    os.makedirs(dst_dir, exist_ok=True)
                    shutil.copy2(
                        os.path.join(root, file),
                        os.path.join(dst_dir, file)
                    )

def create_launcher_script(dist_dir, exe_name):
    """Create a launcher script for the executable"""
    launcher_content = '''#!/bin/bash
# Check if SWI-Prolog is installed
if ! command -v swipl &> /dev/null; then
    echo "Error: SWI-Prolog is not installed. Please install it first."
    echo "Visit: https://www.swi-prolog.org/download/stable"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run the executable with all arguments
"$SCRIPT_DIR/{}" "$@"
'''.format(exe_name)

    launcher_path = os.path.join(dist_dir, 'run_rlgen.sh')
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    os.chmod(launcher_path, 0o755)

def create_windows_launcher(dist_dir, exe_name):
    """Create a Windows batch launcher script"""
    launcher_content = '''@echo off
REM Check if SWI-Prolog is installed
where swipl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: SWI-Prolog is not installed. Please install it first.
    echo Visit: https://www.swi-prolog.org/download/stable
    exit /b 1
)

REM Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"

REM Run the executable with all arguments
"%SCRIPT_DIR%{}" %*
'''.format(exe_name)

    launcher_path = os.path.join(dist_dir, 'run_rlgen.bat')
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)

def build_executable():
    # Get the absolute path to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create dist directory if it doesn't exist
    dist_dir = os.path.join(project_root, 'dist')
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # Create build directory if it doesn't exist
    build_dir = os.path.join(project_root, 'build')
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    # Get platform-specific executable name
    exe_name = get_platform_specific_name()
    
    # Create spec file
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['scripts/main.py'],
    pathex=['{project_root}'],
    binaries=[],
    datas=[
        ('scripts/config.json', 'scripts'),
        ('scripts/QE/DT-Golog.pl', 'scripts/QE'),
    ],
    hiddenimports=[
        'gym',
        'numpy',
        'pyswip',
        'stable_baselines3',
        'stable_baselines3.common',
        'stable_baselines3.common.vec_env',
        'stable_baselines3.common.env_util',
        'stable_baselines3.common.utils',
        'stable_baselines3.common.policies',
        'stable_baselines3.common.torch_layers',
        'stable_baselines3.common.type_aliases',
        'stable_baselines3.common.callbacks',
        'stable_baselines3.common.monitor',
        'stable_baselines3.common.vec_env',
        'stable_baselines3.common.env_checker',
        'stable_baselines3.common.buffers',
        'stable_baselines3.common.save_util',
        'stable_baselines3.common.torch_layers',
        'stable_baselines3.common.type_aliases',
        'stable_baselines3.common.utils',
        'stable_baselines3.common.vec_env',
        'stable_baselines3.common.env_util',
        'stable_baselines3.common.callbacks',
        'stable_baselines3.common.monitor',
        'stable_baselines3.common.vec_env',
        'stable_baselines3.common.env_checker',
        'stable_baselines3.common.buffers',
        'stable_baselines3.common.save_util',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    spec_path = os.path.join(project_root, 'rlgen.spec')
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    # Run PyInstaller
    subprocess.run(['pyinstaller', '--clean', spec_path], check=True)
    
    # Copy required files
    copy_required_files(project_root, dist_dir)
    
    # Create launcher scripts
    if platform.system().lower() == 'windows':
        create_windows_launcher(dist_dir, exe_name)
    else:
        create_launcher_script(dist_dir, exe_name)
    
    # Create README in dist directory
    readme_content = '''RLGen Executable
===============

This is a standalone executable version of RLGen.

Prerequisites:
-------------
1. SWI-Prolog must be installed on your system
   - Download from: https://www.swi-prolog.org/download/stable
   - Make sure it's added to your system PATH

Usage:
------
1. On Windows:
   - Double-click run_rlgen.bat
   - Or run from command line: run_rlgen.bat <pl_file> --mode {simulate,train} --config scripts/config.json

2. On Linux/Mac:
   - Run from terminal: ./run_rlgen.sh <pl_file> --mode {simulate,train} --config scripts/config.json

Example:
--------
./run_rlgen.sh examples/discrete/3Build.pl --mode simulate --config scripts/config.json

Troubleshooting:
---------------
1. If you get "SWI-Prolog not found" error:
   - Make sure SWI-Prolog is installed
   - Verify it's in your system PATH
   - Try running 'swipl --version' in terminal to test

2. If you get "Permission denied":
   - On Linux/Mac: Run 'chmod +x run_rlgen.sh'
   - On Windows: Run as administrator

3. If you get "File not found":
   - Make sure you're running the command from the correct directory
   - Verify the paths to your .pl files are correct
'''
    
    with open(os.path.join(dist_dir, 'README.txt'), 'w') as f:
        f.write(readme_content)
    
    print("\nBuild completed successfully!")
    print(f"Executable and all required files can be found in: {dist_dir}")
    print("\nTo distribute:")
    print("1. Zip the entire 'dist' directory")
    print("2. Share the zip file with users")
    print("3. Users only need to install SWI-Prolog to run the executable")

if __name__ == '__main__':
    build_executable() 