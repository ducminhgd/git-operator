"""Module for manipulating repository services
"""
from typing import Dict, Optional
from gitlab import Gitlab, GitlabGetError
from gitlab.exceptions import GitlabCreateError
from gitlab.v4.objects import Project, ProjectTag, ProjectCommit
from changelog import collect_changelog, bump_version, get_changelog_markdown, get_hotfix_changelog_markdown, get_latest_version


class GitLabRepo:
    """Class for Gitlab
    """
    __connector: Gitlab = None
    __project: Project = None

    def __init__(self, host, token) -> Gitlab:
        """Init handler

        :param host: Repository host
        :type host: str
        :param token: Access Token
        :type token: str
        """
        self.__connector = Gitlab(host, private_token=token)

    def set_project(self, project_id: int) -> Project:
        """Set project as current project

        :param project_id: ID of project on Gitlab
        :type project_id: int
        :return: current project after set
        :rtype: Project
        """
        self.__project = self.__connector.projects.get(project_id)

    def get_tags_as_string(self, project_id: Optional[int] = None) -> Dict[str, ProjectTag]:
        """Get list tags as strings

        :param project_id: ID of project. If None then get from object, defaults to None
        :type project_id: Optional[int], optional
        :return: Dictionary with keys are tags as strings, values are ProjectTag objects
        :rtype: Dict[str, ProjectTag]
        """
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

    def get_commit(self, commit_ref: str = 'master', project_id: Optional[int] = None) -> Optional[ProjectCommit]:
        """Get commit information from commit ref

        :param commit_ref: Ref of commit to fetch, defaults to 'master'
        :type commit_ref: str, optional
        :param project_id: ID of project. If None then get from object, defaults to None
        :type project_id: Optional[int], optional
        :return: Commit object
        :rtype: ProjectCommit or None
        """
        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project
        try:
            return project.commits.get(commit_ref)
        except GitlabGetError as ex:
            return None

    def get_latest_commit(self, project_id: Optional[int] = None) -> Optional[ProjectCommit]:
        """Get latest commit

        :param project_id: ID of project. If None then get from object, defaults to None
        :type project_id: Optional[int], optional
        :return: [description]
        :rtype: Optional[ProjectCommit]
        """
        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project
        commits = project.commits.list(sort='desc')
        if bool(commits):
            return commits[0]
        return None

    def get_diff(self, from_ref: str, to_ref: str = 'master', project_id: Optional[int] = None):
        """Get differences commit between to refs

        :param from_ref: newer ref
        :type from_ref: str
        :param to_ref: older ref, defaults to 'master'
        :type to_ref: str, optional
        :param project_id: ID of project. If None then get from object, defaults to None
        :type project_id: Optional[int], optional
        :return: [description]
        :rtype: [type]
        """
        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project
        return project.repository_compare(from_ref, to_ref)

    def create_version_branch(self, version: str, ref: str, project_id: Optional[int] = None) -> bool:
        """Create a branch with format `release/{version}`

        :param version: Desired version
        :type version: str
        :param ref: Ref to create branch from
        :type ref: str
        :param project_id: ID of project. If None then get from object, defaults to None
        :type project_id: Optional[int], optional
        :return: [description]
        :rtype: bool
        """
        if not bool(version) or not bool(ref):
            print('Invalid version or ref')
            return False

        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project

        try:
            project.branches.create({
                'branch': f'release/{version}',
                'ref': ref,
            })
        except Exception as ex:
            print(f'{str(ex)}: release/{version}')
            return False
        print(f'Create branch release/{version}')
        return True

    def create_tag(self, ref_name: str, desired_version: Optional[str] = None, project_id: Optional[int] = None) -> bool:
        """Create tag from a ref with or without desired version, read more:
        - https://docs.gitlab.com/ee/api/releases/
        - https://docs.gitlab.com/ee/api/tags.html

        :param ref_name: Name of ref to create tag from
        :type ref_name: str
        :param desired_version: Desired version, not need to pass if make it auto, defaults to None
        :type desired_version: Optional[str], optional
        :param project_id: ID of project. If None then get from object, defaults to None
        :type project_id: Optional[int], optional
        :rtype: bool
        """
        version, changes_log = self.get_next_version(ref_name, desired_version)
        if not bool(changes_log):
            print('No changed')
            return False

        if bool(project_id):
            project = self.__connector.projects.get(project_id)
        else:
            project = self.__project

        try:
            project.tags.create({
                'tag_name': f'v{version}',
                'ref': ref_name,
                'release_description': changes_log
            })
        except Exception as ex:
            print(f'{str(ex)}: v{version}')
            return False
        print(f'Create version {version}')
        return True

    def get_next_version(self, ref_name: str = 'master', from_version: Optional[str] = None):
        """Get next version if capable

        :param ref_name: ref name or ref hash to create next version, defaults to 'master'
        :type ref_name: str, optional
        :param from_version: from version it bumps, default is None
        :type from_version: Optional[str], optional
        :return: next version, change log
        :rtype: Tuple(str, str)
        """
        tags = self.get_tags_as_string()

        if bool(from_version):
            latest_vname = from_version
        else:
            latest_vname = get_latest_version(list(tags.keys()))
        if not bool(tags):
            return latest_vname, get_changelog_markdown(latest_vname, {})
        ref = self.get_commit(ref_name)
        if ref is None:
            return None, ''
        latest_tag = self.get_commit(tags[latest_vname].target)
        diff = self.get_diff(from_ref=latest_tag.id, to_ref=ref.id)
        if not bool(diff['commits']):
            return latest_vname, ''
        changelog = collect_changelog(diff)
        new_version = bump_version(
            latest_vname, bool(changelog['Major']),
            bool(changelog['Minor']) or bool(changelog['Missing']),
            bool(changelog['Patch'])
        )
        return new_version, get_changelog_markdown(new_version, changelog)
