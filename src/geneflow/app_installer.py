"""This module contains the GeneFlow App Installer class."""


from pathlib import Path
import pprint
import cerberus
import shutil
from git import Repo
from git.exc import GitError
import os
from slugify import slugify
import stat
import yaml
from slugify import slugify

from geneflow.data_manager import DataManager
from geneflow.definition import Definition
from geneflow.log import Log
from geneflow.shell_wrapper import ShellWrapper
from geneflow.template_compiler import TemplateCompiler
from geneflow.uri_parser import URIParser


class AppInstaller:
    """
    GeneFlow AppInstaller class.

    The AppInstaller class is used to download, generate, and install apps
    from a GeneFlow git repo.
    """

    def __init__(
            self,
            path,
            app_info
    ):
        """
        Initialize the GeneFlow AppInstaller class.

        Args:
            self: class instance
            path: local path to the app package
            app_info: app information from workflow definition (name, git repo, version)

        Returns:
            None

        """
        self._path = Path(path)
        self._app_info = app_info

        # app definition, which should be in the root of the app package
        self._app = None


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


    def clone_git_repo(self):
        """
        Clone app from git repo.

        Args:
            self: class instance

        Returns:
            On success: True
            On failure: False

        """
        # remove app folder if it exists
        if self._path.is_dir():
            shutil.rmtree(str(self._path))

        # recreate app folder
        self._path.mkdir()

        # clone app's git repo into target location
        try:
            if self._app_info['version']:
                Repo.clone_from(
                    self._app_info['git'], str(self._path), branch=self._app_info['version'],
                    config='http.sslVerify=false'
                )
            else:
                Repo.clone_from(
                    self._app_info['git'], str(self._path),
                    config='http.sslVerify=false'
                )
        except GitError as err:
            Log.an().error(
                'cannot clone app git repo: %s [%s]',
                self._app_info['git'], str(err)
            )
            return False

        return True


    def write_app_yaml(self):
        ## write out an app.yaml file based on what's in _app_info

        # create app folder
        self._path.mkdir(exist_ok=True)

        app_yaml_path = str(Path(self._path / 'app.yaml'))

        try:
            with open(app_yaml_path, 'w') as yaml_file:
                yaml.dump(self._app_info, yaml_file)
        except yaml.YAMLError as err:
            Log.an().warning('error writing yaml file: %s', app_yaml_path)
            return False

        return True


    def load_app(self):
        """
        Load app definition.

        Args:
            self: class instance

        Returns:
            On success: True
            On failure: False

        """
        # read yaml file
        self._app = self._yaml_to_dict(
            str(Path(self._path / 'app.yaml'))
        )

        # empty dict?
        if not self._app:
            Log.an().error(
                'cannot load/parse app.yaml file in app: %s', self._path
            )
            return False

        valid_def = Definition.validate_app(self._app)
        if not valid_def:
            Log.an().error('app validation error')
            return False

        return True


    def make(self):
        """
        Generate GeneFlow app files from templates.

        Args:
            self: class instance

        Returns:
            On success: True
            On failure: False

        """
        if not self.make_wrapper():
            return False
        if not self.make_test():
            return False

        return True


    def update_def(self):
        """
        Update GeneFlow app definition by adding the implementation section.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        Log.some().info('updating %s', str(self._path / 'app.yaml'))

        try:
            with open(str(self._path / 'app.yaml'), 'a') as app_yaml:
                app_yaml.write('\n\nimplementation:')
                app_yaml.write('\n  local:')
                app_yaml.write(
                    '\n    script: {}.sh'.format(slugify(self._app['name'], regex_pattern=r'[^-a-z0-9_]+'))
                )
        except IOError as err:
            Log.an().error('cannot update GeneFlow app definition: %s', err)
            return False

        return True


    def make_wrapper(self):
        """
        Generate the GeneFlow app wrapper script.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        # make assets folder, if it doesn't already exist
        asset_path = Path(self._path / 'assets')
        asset_path.mkdir(exist_ok=True)

        script_path = str(asset_path / '{}.sh'.format(slugify(self._app['name'], regex_pattern=r'[^-a-z0-9_]+')))
        Log.some().info('compiling %s', script_path)

        # compile jinja2 template
        if not TemplateCompiler.compile_template(
                None,
                'wrapper-script.sh.j2',
                script_path,
                **self._app
        ):
            Log.an().error('cannot compile GeneFlow app wrapper script')
            return False

        # make script executable by owner
        os.chmod(script_path, stat.S_IRWXU)

        return True


    def make_test(self):
        """
        Generate the GeneFlow app test script.

        Args:
            self: class instance

        Returns:
            On success: True.
            On failure: False.

        """
        # make test folder, if it doesn't already exist
        test_path = Path(self._path / 'test')
        test_path.mkdir(exist_ok=True)

        script_path = str(test_path / 'test.sh')
        Log.some().info('compiling %s', script_path)

        # compile jinja2 template
        if not TemplateCompiler.compile_template(
                None,
                'test.sh.j2',
                script_path,
                **self._app
        ):
            Log.an().error('cannot compile GeneFlow app test script')
            return False

        # make script executable by owner
        os.chmod(script_path, stat.S_IRWXU)

        return True
