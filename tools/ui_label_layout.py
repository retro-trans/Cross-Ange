"""Fit shared English UI labels to columns measured in actual game captures."""
import json
from pathlib import Path

import build_english_font as font

ROOT = Path(__file__).resolve().parents[1]


def compact_labels(interface):
    data = json.loads((ROOT / 'work/translation/en/ui-compact-labels.en.json').read_text(encoding='utf-8'))
    layout = json.loads((ROOT / 'work/ui/briefing-label-layout.json').read_text(encoding='utf-8'))
    rows = {row['id']: row for row in interface['entries']}
    overrides = {}
    for entry in data['entries']:
        identity = entry['id'], entry['column']
        row = rows[entry['id']]
        field = row['fields'][entry['column']]
        if identity in overrides or row['key'] != entry['key'] or field['en'] != entry['canonical_en']:
            raise ValueError('Compact UI label identity/canonical wording changed')
        if not entry['display_en']:
            raise ValueError('Empty compact UI label')
        overrides[identity] = entry['display_en']
    measurements = []
    for contract in layout['label_contracts']:
        for identifier in contract['ids']:
            text = overrides.get((identifier, 0), rows[identifier]['fields'][0]['en'])
            width = font.measure(text) * contract['font_size_for_validation'] / font.FONT_SIZE
            available = contract['next_column_x'] - contract['label_x'] - contract['minimum_gap']
            if width > available:
                raise ValueError('English UI label crosses adjacent column: ' + str(identifier))
            measurements.append({'id': identifier, 'display_en': text, 'width': width,
                                 'available_width': available, 'contract': contract['name']})
    unit = overrides[(layout['concatenated_unit_id'], 0)]
    if not unit.startswith(' ') or unit.strip() != rows[layout['concatenated_unit_id']]['fields'][0]['en']:
        raise ValueError('Concatenated time unit lost its separator or wording')
    for contract in layout.get('separated_units', []):
        unit = overrides[(contract['id'], 0)]
        if not unit.startswith(' ') or contract['sample_number'] + unit != contract['expected']:
            raise ValueError('Compact time unit lost its numeric separator')
    return overrides, {'display_adaptations': len(overrides), 'canonical_drafts_unchanged': True,
                       'measurements': measurements, 'entries': data['entries'],
                       'layout_record': 'work/ui/briefing-label-layout.json',
                       'runtime_verified': layout['fix_runtime_verified']}
