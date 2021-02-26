# Git Operator

Using for manage projects on Git repositories

- [X] Gitlab
- [ ] Github

## Usage

```bash
usage: main.py [-h] [--host HOST] [--token TOKEN] [--ref REF]
               [--version VERSION] [--send-to SEND_TO] [--send-cc SEND_CC]
               [--send-bcc SEND_BCC]
               {gitlab,github} project_id {create-branch,tag,release,send}

Git operator service

positional arguments:
  {gitlab,github}       Service name
  project_id            ID of Project
  {create-branch,tag,release,send}
                        Command

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Git host
  --token TOKEN         Token for authentication
  --ref REF             Ref name or commit hash
  --version VERSION     Desired version
  --send-to SEND_TO     Email address to send email to
  --send-cc SEND_CC     Email address to send CC email to
  --send-bcc SEND_BCC   Email address to send BCC email to
```

Need declare environment variables

```
ENV=
GIT_HOST=
GIT_PRIVATE_TOKEN=

SMTP_SERVER=
SMTP_USERNAME=
SMTP_PASSWORD=
```

## Commit message convention

1. A commit message SHOULD contain a tag:
  - Major tags are `#breaking`, `#major`, `#remove`/`#removed`, `#revert`/`#reverted`, `#upgrade`/`#upgrade`, which changes make current application make it not compatible
  - Minor tags are: `#minor`, `#change`/`#changed`,  `#add`/`#added`, `#update`/`#updated`
  - Patch tags are: `#patch`/`#patched`, `#fix`/`#fixed`, `#hotfix`/`#hotfixed`, `#bugfix`/`#bugfixed`
2. If commit message DOES NOT contain a tag, then consider as `#minor`