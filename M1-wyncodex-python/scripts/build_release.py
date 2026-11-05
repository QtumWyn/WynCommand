"""Build a Linux one-folder application and separate versioned content download."""
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
import sysconfig
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from wyncodex.config import APPLICATION_VERSION
from wyncodex.services.library_update_service import load_package

if platform.system() != 'Linux' or platform.machine() != 'x86_64':
    raise SystemExit('This release script targets Linux x86_64.')
document = load_package()
subprocess.run([sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', 'WynCodex.spec'], cwd=ROOT, check=True)
bundle = ROOT / 'dist/WynCodex'
shutil.copy2(ROOT / 'README.txt', bundle / 'README.txt')
licenses = bundle / 'THIRD_PARTY_LICENSES'
licenses.mkdir(exist_ok=True)
for name in ('LGPL-3', 'GPL-3', 'GPL-2', 'LGPL-2.1'):
    shutil.copy2(Path('/usr/share/common-licenses') / name, licenses / (name + '.txt'))
for package in ('Pygments', 'PyInstaller'):
    distribution = importlib.metadata.distribution(package)
    for path in distribution.files or []:
        if 'licenses/' in str(path):
            source = Path(distribution.locate_file(path))
            if source.is_file():
                shutil.copy2(source, licenses / (package + '-' + source.name))
python_license = Path(sysconfig.get_path('stdlib')) / 'LICENSE.txt'
if python_license.is_file():
    shutil.copy2(python_license, licenses / 'Python-LICENSE.txt')
else:
    # CPython's installed site printer searches its own distribution license.
    import builtins
    builtins.license._Printer__setup()
    (licenses / 'Python-LICENSE.txt').write_text('\n'.join(builtins.license._Printer__lines) + '\n')
notices = '''Third-party components

Python: Python Software Foundation and contributors; see Python-LICENSE.txt.
https://www.python.org/downloads/source/

PySide6, Shiboken6 and Qt 6.11.2: The Qt Company Ltd and contributors.
The installed PySide6/Shiboken6 distributions state
LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only.
Included shared Qt libraries remain dynamically linked in _internal.
The LGPL/GPL license texts are included. Compatible replacement libraries can be
placed in that directory; keep any replacements and their notices together.
Upstream source and module licensing:
https://code.qt.io/cgit/pyside/pyside-setup.git/
https://code.qt.io/cgit/qt/qtbase.git/
https://doc.qt.io/qt-6/licensing.html

Pygments: the Pygments team; see Pygments-LICENSE and Pygments-AUTHORS.
https://pygments.org/

PyInstaller: see PyInstaller-COPYING.txt, including its bootloader exception.
https://pyinstaller.org/

Additional system shared libraries retain their upstream licenses. This bundle
also includes the build system's Debian copyright notices where available.
'''
(bundle / 'THIRD_PARTY_NOTICES.txt').write_text(notices)
copyrights = licenses / 'system'
copyrights.mkdir(exist_ok=True)
# Preserve installed copyright notices for bundled system libraries.
packages = set()
patterns = sorted({'*/' + path.name for path in bundle.rglob('*.so*') if path.is_file()})
if patterns:
    result = subprocess.run(['dpkg-query', '-S', *patterns], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if ': /' in line:
            packages.add(line.split(': /', 1)[0].split(':', 1)[0])
for package in sorted(packages):
    source = Path('/usr/share/doc') / package / 'copyright'
    if source.is_file():
        shutil.copy2(source, copyrights / (package + '.txt'))
release = ROOT / 'dist/release'
release.mkdir(exist_ok=True)
archive = release / f'WynCodex-v{APPLICATION_VERSION}-linux-x86_64.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
    for path in sorted(bundle.rglob('*')):
        if path.is_file():
            output.write(path, path.relative_to(bundle.parent))
library = release / f'WynCodex-public-library-{document["version"]}.json'
shutil.copy2(ROOT / 'src/wyncodex/resources/public-library.json', library)
info = {
    'application_version': APPLICATION_VERSION,
    'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'python': platform.python_version(),
    'build_platform': platform.platform(),
    'glibc': platform.libc_ver(),
    'dependencies': {name: importlib.metadata.version(name) for name in ('PySide6', 'Pygments', 'PyInstaller')},
    'library_version': document['version'],
    'library_content_sha256': document['content_sha256'],
    'library_counts': {table: len(rows) for table, rows in document['records'].items()},
}
(release / 'BUILD-INFO.json').write_text(json.dumps(info, indent=2) + '\n')
files = [archive, library, release / 'BUILD-INFO.json']
(release / 'SHA256SUMS').write_text(''.join(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n' for path in files))
print(json.dumps(info, indent=2))
