"""Fit operation briefings without changing their wording or color controls."""
import json
import re
from pathlib import Path

import build_english_font as font

ROOT = Path(__file__).resolve().parents[1]
KEY = re.compile(r'STR_BRIEFING_(?:MISSION_\d\d_\d|HEROINE_MISSION_\d\d|SUB_MISSION_\d\d)')


def non_layout_controls(text):
    return font.CONTROL.findall(text.replace('#n', ' '))


def visible(text):
    return re.sub(r'\s+', '', font.CONTROL.sub('', text))


def fit(text, width, maximum_lines):
    original = text.split('#n')
    if all(font.measure(line) <= width for line in original) and len(original) <= maximum_lines:
        return text
    lines, paragraph = [], []

    def flush():
        if paragraph:
            lines.extend(font._wrap(' '.join(paragraph).split(), width))
            paragraph.clear()

    for part in original:
        if not part.strip():
            flush()
            lines.append(' ')
        elif part.startswith('#c'):
            flush()
            paragraph.append(part)
        else:
            paragraph.append(part)
    flush()
    result = '#n'.join(lines)
    if len(lines) > maximum_lines or any(font.measure(line) > width for line in lines):
        raise ValueError('Briefing exceeds its panel; edit the translation before building')
    if visible(result) != visible(text) or non_layout_controls(result) != non_layout_controls(text):
        raise ValueError('Briefing layout changed wording or non-layout controls')
    return result


def descriptions(interface):
    contract = json.loads((ROOT / 'work/ui/briefing-body-layout.json').read_text(encoding='utf-8'))
    overrides, entries = {}, []
    for row in interface['entries']:
        if not KEY.fullmatch(row.get('key') or ''):
            continue
        field = row['fields'][0]
        text = field['en']
        try:
            fitted = fit(text, contract['width_limit'], contract['maximum_lines'])
        except ValueError as error:
            raise ValueError(str(error) + ': ' + row['key']) from error
        overrides[row['id'], 0] = fitted
        lines = fitted.split('#n')
        entries.append(dict(id=row['id'], key=row['key'], canonical_en=text, display_en=fitted,
                            changed=fitted != text, lines=len(lines),
                            maximum_width=max(map(font.measure, lines)),
                            original_maximum_width=max(map(font.measure, text.split('#n')))))
    if len(entries) != contract['expected_descriptions']:
        raise ValueError('Briefing inventory changed; review its layout contract')
    return overrides, dict(descriptions_checked=len(entries), reflowed=sum(r['changed'] for r in entries),
                          width_limit=contract['width_limit'], maximum_lines=contract['maximum_lines'],
                          wording_and_non_layout_controls_preserved=True, runtime_verified=False,
                          layout_record='work/ui/briefing-body-layout.json', entries=entries)
