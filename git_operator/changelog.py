import semver
from typing import Dict

TAG_TYPE = {
    '#breaking': 'Major',
    '#major': 'Major',
    '#remove': 'Major',
    '#removed': 'Major',
    '#revert': 'Major',
    '#reverted': 'Major',
    '#upgrad': 'Major',
    '#upgraded': 'Major',
    '#minor': 'Minor',
    '#change': 'Minor',
    '#changed': 'Minor',
    '#add': 'Minor',
    '#added': 'Minor',
    '#update': 'Minor',
    '#updated': 'Minor',
    '#patch': 'Patch',
    '#patched': 'Patch',
    '#fix': 'Patch',
    '#fixed': 'Patch',
    '#hotfix': 'Patch',
    '#hotfixed': 'Patch',
    '#bugfix': 'Patch',
    '#bugfixed': 'Patch',
}


def get_latest_version(version_list: list) -> str:
    if not bool(version_list):
        return '1.0.0'
    list_len = len(version_list)
    if list_len == 1:
        return version_list[0]
    max_ver = version_list[0]
    for ver in version_list:
        max_ver = semver.max_ver(ver, max_ver)
    return max_ver


def collect_changelog(diff: Dict) -> Dict:
    result = {
        'Major': [],
        'Minor': [],
        'Patch': [],
        'Missing': [],
    }
    for commit in diff['commits']:
        for tag, typ in TAG_TYPE.items():
            if tag in commit['title'].lower():
                result[typ].insert(0, commit)
                break
        else:
            result['Missing'].insert(0, commit)
    return result


def bump_version(current: str, major: bool = False, minor: bool = False, patch: bool = False):
    if major:
        return semver.bump_major(current)
    if minor:
        return semver.bump_minor(current)
    if patch:
        return semver.bump_patch(current)
    return current


def get_changelog_markdown(ver: str, changelog: Dict) -> str:
    changelog_lines = [f'# Release version {ver}', ]

    if bool(changelog['Major']):
        semver.bump_major(current_version)
        changelog_lines.append('## Major changes')
        for line in changelog['Major']:
            changelog_lines.append(f'- {line["title"]}')
    if bool(changelog['Minor']):
        changelog_lines.append('## Minor changes')
        for line in changelog['Minor']:
            changelog_lines.append(f'- {line["title"]}')
    if bool(changelog['Patch']):
        changelog_lines.append('## Patches')
        for line in changelog['Patch']:
            changelog_lines.append(f'- {line["title"]}')
    if bool(changelog['Missing']):
        changelog_lines.append('## Missing definition')
        for line in changelog['Missing']:
            changelog_lines.append(f'- {line["title"]}')
    if bool(changelog_lines):
        return '\n\n'.join(changelog_lines)
    return ''
