import os
import argparse
from repository import GitLabRepo
from email_helper import send_email

ENV = os.getenv('ENV', 'Production')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Git operator service')
    parser.add_argument('service', help='Service name', choices=['gitlab', 'github'])
    parser.add_argument('project_id', help='ID of Project', type=int)
    parser.add_argument('command', help='Command', choices=['create-branch', 'tag', 'release', 'send'])

    parser.add_argument('--host', help='Git host', required=False, dest='host', default=os.getenv('GIT_HOST', ''))
    parser.add_argument('--token', help='Token for authentication', required=False,
                        dest='token', default=os.getenv('GIT_PRIVATE_TOKEN', ''))
    parser.add_argument('--ref', help='Ref name or commit hash', required=False, dest='ref')
    parser.add_argument('--version', help='Desired version', required=False, dest='version')
    parser.add_argument('--send-to', help='Email address to send email to', required=False, dest='send_to')
    parser.add_argument('--send-cc', help='Email address to send CC email to', required=False, dest='send_cc')
    parser.add_argument('--send-bcc', help='Email address to send BCC email to', required=False, dest='send_bcc')

    args = parser.parse_args()
    if not bool(args.host):
        host = 'https://gitlab.com'
    service = GitLabRepo(args.host, args.token)
    service.set_project(args.project_id)

    if not(args.ref):
        ref_name = 'master'
    else:
        ref_name = args.ref

    if args.command == 'create-branch' or args.command == 'release':
        version, changes_log = service.get_next_version(ref_name, args.version)
        if version is None:
            exit(1)
        success = service.create_version_branch(version, ref_name)
        if not success:
            exit(1)

    if args.command == 'tag' or args.command == 'release':
        success = service.create_tag(ref_name, args.version)
        if not success:
            exit(1)

    if args.command == 'send':
        project = service.get_project(args.project_id)
        tag = service.get_tag(ref_name, args.project_id)
        if not tag or not project:
            print('Project or Tag does not exit')
            exit(1)
        subject = f'[{ENV}][{project.path_with_namespace}] Release version {tag.name} ({tag.target})'
        body = tag.release.get('description', f'Commit hash: {tag.target}')
        sent_email = send_email(args.send_to, subject, body, args.send_cc, args.send_bcc)
        if not sent_email:
            print('Send email failed')
            exit(1)

    exit(0)
