# Git Operator

Using for manage projects on Git repositories

- [X] Gitlab
- [ ] Github

## Usage

```bash
usage: main.py [-h] [--host HOST] [--token TOKEN] [--ref REF] {gitlab,github} {release} project_id

Git operator service

positional arguments:
  {gitlab,github}  Service name
  {release}        Command
  project_id       ID of Project

optional arguments:
  -h, --help       show this help message and exit
  --host HOST      Git host
  --token TOKEN    Token for authentication
  --ref REF        Ref name or commit hash
```

## Commit message convention

1. A commit message SHOULD contain a tag:
  - Majour tags are `#removed`, `#reverted`, `#upgrade`, which changes make current application make it not compatible
  - Minor tags are: `#changed`,  `#added`, `#updated`
  - Patch tags are: `#patched`, `#fixed`, `#hotfixed`, `#bugfixed`
2. If commit message DOES NOT contain a tag, then consider as `#patched`