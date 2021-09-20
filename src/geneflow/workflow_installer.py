"""This module contains the GeneFlow Workflow installer class."""


import shutil
from pathlib import Path
import pprint
import yaml

from git import Repo
from git.exc import GitError
import requests
from slugify import slugify

from geneflow.app_installer import AppInstaller
from geneflow.data_manager import DataManager
from geneflow.definition import Definition
from geneflow.log import Log
from geneflow.template_compiler import TemplateCompiler
from geneflow.uri_parser import URIParser


requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


class WorkflowInstaller:
    """
    GeneFlow WorkflowInstaller class.

    The WorkflowInstaller class is used to download and install workflows
    from a GeneFlow git repo.
    """

    def __init__(
            self,
            path,
            git=None,
            git_branch=None,
            force=False,
            app_name=None,
            clean=False,
            config=None,
            make_apps=True
    ):
        """
        Initialize the GeneFlow WorkflowInstaller class.

        Args:
            self: class instance
            path: local path to the workflow package
            git: git repo to clone
            git_branch: branch or tag of git repo
            force: delete existing folder before install?
            app_name: name of app to install
            clean: delete apps folder before install?
            config: GeneFlow config dict
            make_apps: compile app templates

        Returns:
            None

        """
        self._path = path
        self._git = git
        self._git_branch = git_branch
        self._force = force
        self._app_name = app_name
        self._clean = clean
        self._make_apps = make_apps

        self._workflow_yaml = None

        self._config = config


    def initialize(self):
        """
        Initialize the GeneFlow WorkflowInstaller class.

        Initialize the class by cloning the workflow, validating the
        structure, loading apps config.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        # clone workflow
        if self._git:
            if not self._clone_workflow():
                Log.an().error('cannot clone workflow from %s', self._git)
                return False

        # validate workflow structure
        if not self._validate_workflow_package():
            Log.an().error('invalid workflow package at %s', self._path)
            return False

        # load workflow definition
        if not self._load_workflow_def():
            Log.an().error('cannot load workflow definition from %s', self._workflow_yaml)
            return False

        return True


    def _validate_workflow_package(self):

        package_path = Path(self._path)
        if not Path(package_path).is_dir():
            Log.an().error('workflow package path is not a directory: %s', package_path)
            return False

        self._workflow_yaml = Path(package_path / 'workflow.yaml')

        if not self._workflow_yaml.is_file():
            Log.an().error('missing workflow.yaml file in workflow package')
            return False

        return True


    def _load_workflow_def(self):

        # load geneflow definition file
        gf_def = Definition()
        if not gf_def.load(str(self._workflow_yaml)):
            Log.an().error('invalid geneflow definition: %s', self._workflow_yaml)
            return False

        # make sure there is a workflow definition in the file
        if not gf_def.workflows():
            Log.an().error('no workflows in geneflow definition')
            return False

        # extract the workflow definition
        self._workflow = next(iter(gf_def.workflows().values()))

        return True


    @classmethod
    def _yaml_to_dict(cls, path):

        # read yaml file
        try:
            with open(path, 'rU') as yaml_file:
                yaml_data = yaml_file.read()
        except IOError as err:
            Log.an().warning('cannot read yaml file: %s [%s]', path, str(err))
            return False

        # convert to dict
        try:
            yaml_dict = yaml.safe_load(yaml_data)
        except yaml.YAMLError as err:
            Log.an().warning('invalid yaml file: %s [%s]', path, str(err))
            return False

        return yaml_dict


    def _clone_workflow(self):

        if not self._git:
            Log.an().error('must specify a git url to clone workflow')
            return False

        if self._force:
            # remove workflow folder if it exists
            if Path(self._path).is_dir():
                shutil.rmtree(self._path)

        try:
            if self._git_branch:
                Repo.clone_from(
                    self._git, self._path, branch=self._git_branch,
                    config='http.sslVerify=false'
                )
            else:
                Repo.clone_from(
                    self._git, self._path,
                    config='http.sslVerify=false'
                )

        except GitError as err:
            Log.an().error(
                'cannot clone git repo: %s [%s]', self._git, str(err)
            )
            return False

        return True


    def install_apps(self):
        """
        Install apps for the workflow package.

        Args:
            self: class instance.

        Returns:
            None

        """
        apps_path = Path(self._path) / 'apps'
        if self._clean:
            # remove apps folder
            if apps_path.is_dir():
                shutil.rmtree(str(apps_path))

        # create apps folder if not already there
        apps_path.mkdir(exist_ok=True)

        for app in self._workflow['apps']:
            if self._app_name == app or not self._app_name:

                Log.some().info(
                    'app: %s', app
                )

                # determine path to install app
                repo_path = apps_path / slugify(app, regex_pattern=r'[^-a-z0-9_]+')

                # create AppInstaller instance
                app_installer = AppInstaller(
                    str(repo_path),
                    {
                        'name': app,
                        'gfVersion': self._workflow['gfVersion'],
                        'class': 'app',
                        **self._workflow['apps'][app]
                    }
                )

                # check if git and/or version fields are there
                if (self._workflow['apps'][app]['git']):
                    Log.some().info(
                        'app from git repo: %s:%s [%s]',
                        app,
                        self._workflow['apps'][app]['git'],
                        self._workflow['apps'][app]['version']
                    )

                    # clone app into install location
                    if not app_installer.clone_git_repo():
                        Log.an().error('cannot clone app to %s', str(repo_path))
                        return False

                else: 
                    Log.some().info(
                        'app from inline definition: %s',
                        app
                    )

                    # write app.yaml based on inline definition
                    if not app_installer.write_app_yaml():
                        Log.an().error('cannot write app yaml')
                        return False

                if not app_installer.load_app():
                    Log.an().error('cannot load app config')
                    return False

                if self._make_apps:
                    if not app_installer.make():
                        Log.an().error('cannot compile app templates')
                        return False

                # update app definition with implementation section
                if not app_installer.update_def():
                    Log.an().error(
                        'cannot update app "%s" definition',
                        app
                    )
                    return False

        return True
