from typing import Dict, Optional
from gitlab import Gitlab, GitlabGetError
from gitlab.v4.objects import Project, ProjectTag, ProjectCommit
from changelog import collect_changelog, bump_version, get_changelog_markdown


class GitLabRepo:
    __connector: Gitlab = None
    __project: Project = None

    def __init__(self, host, token) -> Gitlab:
        self.__connector = Gitlab(host, private_token=token)

    def set_project(self, project_id: int) -> Project:
        self.__project = self.__connector.projects.get(project_id)

    def get_tags_as_string(self, project_id: Optional[int] = None) -> Dict[str, ProjectTag]:
        result = {}
        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project
        records = project.tags.list()
        for record in records:
            sem_ver = record.name.lstrip('v')
            result[sem_ver] = record
        return result

    def get_commit(self, commit_ref: str = 'master', project_id: Optional[int] = None) -> ProjectCommit:
        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project
        try:
            return project.commits.get(commit_ref)
        except GitlabGetError as ex:
            return None

    def get_latest_commit(self, project_id: Optional[int] = None) -> ProjectCommit:
        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project
        commits = project.commits.list(sort='desc')
        if bool(commits):
            return commits[0]
        return None

    def get_diff(self, from_ref: str, to_ref: str = 'master', project_id: Optional[int] = None):
        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project
        return project.repository_compare(from_ref, to_ref)

    def create_first_release(self, version: str = '1.0.0', project_id: Optional[int] = None) -> bool:
        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project

        try:
            project.branches.create({
                'branch': f'release/{version}',
                'ref': 'master',
            })
        except Exception as ex:
            print(f'{str(ex)}: release/{version}')
            return False
        
        try:
            project.tags.create({
                'tag_name': f'v{version}',
                'ref': 'master',
            })
        except Exception as ex:
            print(f'{str(ex)}: v{version}')
            return False
        
        try:
            project.releases.create({
                'name': f'Release {version}',
                'tag_name': f'v{version}',
                'description': 'Init release',
            })
        except Exception as ex:
            print(f'{str(ex)}: {version}')
            return False
        return True

    def create_release(self, from_ref: ProjectCommit, current_ver: str, diff: Dict, project_id: Optional[int] = None) -> bool:
        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project

        changelog = collect_changelog(diff)
        new_version = bump_version(current_ver, bool(changelog['Major']), bool(
            changelog['Minor']) or bool(changelog['Missing']), bool(changelog['Patch']))
        release_description = get_changelog_markdown(new_version, changelog)

        try:
            project.branches.create({
                'branch': f'release/{new_version}',
                'ref': from_ref.id,
            })
        except Exception as ex:
            print(f'{str(ex)}: release/{new_version}')
            return False
        
        try:
            project.tags.create({
                'tag_name': f'v{new_version}',
                'ref': from_ref.id,
                'release_description': release_description
            })
        except Exception as ex:
            print(f'{str(ex)}: v{new_version}')
            return False
        
        return True