import os
import argparse
from repository import GitLabRepo
from changelog import get_latest_version


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Git operator service')
    parser.add_argument('service', help='Service name', choices=['gitlab', 'github'])
    parser.add_argument('--host', help='Git host', required=False, dest='host', default=os.getenv('GIT_HOST', ''))
    parser.add_argument('--token', help='Token for authentication', required=False,
                        dest='token', default=os.getenv('GIT_PRIVATE_TOKEN', ''))
    parser.add_argument('--ref', help='Ref name or commit hash', required=False, dest='ref', default='master')
    parser.add_argument('command', help='Command', choices=['release', ])
    parser.add_argument('project_id', help='ID of Project', type=int)

    args = parser.parse_args()
    if not bool(args.host):
        host = 'https://gitlab.com'
    service = GitLabRepo(args.host, args.token)
    service.set_project(args.project_id)
    tags = service.get_tags_as_string()
    latest_vname = get_latest_version(list(tags.keys()))
    if not bool(tags):
        success = service.create_first_release(latest_vname)
        exit(1 - int(success))
    latest_v = tags[latest_vname]

    latest_commit = service.get_commit(latest_v.target)
    if bool(args.ref):
        ref = service.get_commit(args.ref)
    else:
        ref = service.get_latest_commit()

    if ref is None:
        print('Cannot find ref')
        exit(0)

    diff = service.get_diff(to_ref=ref.id, from_ref=latest_commit.id)

    if not bool(diff['commits']):
        print('There is no change')
        exit(0)

    success = service.create_release(ref, latest_vname, diff)
    exit(1 - int(success))
