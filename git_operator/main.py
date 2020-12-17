import os
import argparse
from repository import GitLabRepo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Git operator service')
    parser.add_argument('service', help='Service name', choices=['gitlab', 'github'])
    parser.add_argument('project_id', help='ID of Project', type=int)
    parser.add_argument('command', help='Command', choices=['create-branch', 'tag', 'release'])

    parser.add_argument('--host', help='Git host', required=False, dest='host', default=os.getenv('GIT_HOST', ''))
    parser.add_argument('--token', help='Token for authentication', required=False,
                        dest='token', default=os.getenv('GIT_PRIVATE_TOKEN', ''))
    parser.add_argument('--ref', help='Ref name or commit hash', required=False, dest='ref')
    parser.add_argument('--version', help='Desired version', required=False, dest='version')

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
    exit(0)