"""List Markdown headings or read a bounded section without following links."""
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def headings(lines):
    found, fence = [], None
    for index, line in enumerate(lines):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        match = re.match(r'^ {0,3}(#{1,6})\s+(.+?)\s*$', line)
        if match:
            title = re.sub(r'\s+#+\s*$', '', match[2])
            found.append((index, len(match[1]), title))
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', help='Project-relative Markdown file')
    parser.add_argument('--section', help='Exact, unique heading title; omit to list headings')
    parser.add_argument('--start-line', type=int, help='Absolute source line for continuation')
    parser.add_argument('--max-lines', type=int, default=80)
    args = parser.parse_args()
    if not 1 <= args.max_lines <= 200:
        parser.error('--max-lines must be between 1 and 200')
    if args.start_line is not None and (args.section is None or args.start_line < 1):
        parser.error('--start-line requires --section and a positive line number')
    try:
        path = (ROOT / args.path).resolve()
        path.relative_to(ROOT.resolve())
        if path.suffix.lower() != '.md':
            raise ValueError('Only Markdown files are supported')
        lines = path.read_text(encoding='utf-8').splitlines()
        titles = headings(lines)
        if args.section is None:
            outline = '\n'.join(f'{i + 1}: {"#" * level} {title}' for i, level, title in titles)
            print(outline[:12000] or '[No ATX headings found.]')
            if len(outline) > 12000:
                print('[Heading list truncated at 12000 characters; inspect the file by line range.]')
            return 0
        matches = [item for item in titles if item[2] == args.section]
        if len(matches) != 1:
            raise ValueError('Section must match exactly one heading; list headings first')
        start, level, _ = matches[0]
        end = next((i for i, depth, _ in titles if i > start and depth <= level), len(lines))
        if args.start_line is not None:
            if not start <= args.start_line - 1 < end:
                raise ValueError('--start-line is outside the selected section')
            start = args.start_line - 1
        print(f'{path.relative_to(ROOT)} | section={args.section} | lines {start + 1}-{end}')
        used = 0
        for i in range(start, min(end, start + args.max_lines)):
            text = f'{i + 1}: {lines[i]}'
            if used + len(text) + 1 > 12000:
                print(f'[Character limit reached at line {i + 1}; inspect that line separately.]')
                return 0
            print(text)
            used += len(text) + 1
        if start + args.max_lines < end:
            print(f'[More: use --start-line {start + args.max_lines + 1} with the same section.]')
        return 0
    except (OSError, ValueError) as exc:
        parser.exit(2, f'Cannot read document: {exc}\n')


if __name__ == '__main__':
    sys.exit(main())
