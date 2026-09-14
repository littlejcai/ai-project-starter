"""Regenerate the starter distribution manifest. Use only while maintaining the template."""
import hashlib

from check_template import ROOT
from doctor import distribution_files
from project_config import lifecycle, load_config, validate


def main():
    config = load_config(ROOT)
    validate(config)
    if lifecycle(config)['stage'] != 'template':
        raise SystemExit('Refusing to update a template distribution manifest outside template stage.')
    lines = []
    for path in distribution_files(ROOT):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f'{digest}  {path.relative_to(ROOT)}')
    (ROOT / 'MANIFEST.sha256').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Updated MANIFEST.sha256 with {len(lines)} files.')


if __name__ == '__main__':
    main()
