"""This module contains methods for the install-workflow CLI command."""


from pathlib import Path
import yaml

from geneflow.config import Config
from geneflow.log import Log
from geneflow.workflow_installer import WorkflowInstaller


def init_subparser(subparsers):
    """
    Initialize argument sub-parser for install-workflow sub-command.

    Args:
        subparsers: list of argparse subparsers

    Returns:
        None

    """
    parser = subparsers.add_parser(
        'install-workflow', help='install workflow'
    )
    parser.add_argument(
        'workflow_path',
        type=str,
        help='GeneFlow workflow package path'
    )
    parser.add_argument(
        '-g', '--git',
        type=str,
        required=False,
        default=None,
        help='URL of git repo from which to clone workflow'
    )
    parser.add_argument(
        '--git-branch',
        type=str,
        required=False,
        default=None,
        dest='git_branch',
        help='git tag or branch to clone'
    )
    parser.add_argument(
        '-f', '--force', action='store_true',
        required=False,
        help='Overwrite existing workflow folder'
    )
    parser.add_argument(
        '-n', '--name',
        type=str,
        required=False,
        default=None,
        help='Name of app to install. If omitted, all apps are installed'
    )
    parser.add_argument(
        '-c', '--clean', action='store_true',
        required=False,
        help='Clean apps folder before install'
    )
    parser.set_defaults(clean=False)
    parser.add_argument(
        '--make-apps', action='store_true',
        required=False,
        default=None,
        dest='make_apps',
        help='Auto-generate app files during install'
    )
    parser.set_defaults(make_apps=False)
    parser.add_argument(
        '--config',
        type=str,
        required=False,
        default=None,
        help='GeneFlow config file'
    )
    parser.add_argument(
        '-e', '--environment',
        type=str,
        required=False,
        default=None,
        help='config environment'
    )
    parser.set_defaults(func=install_workflow)

    return parser


def install_workflow(args, other_args, subparser=None):
    """
    Install a GeneFlow workflow.

    Args:
        args: contains all command-line arguments.

    Returns:
        On success: True.
        On failure: False.

    """
    # load config if specified
    config_dict = None
    cfg = Config()
    if args.config:
        if not args.environment:
            Log.an().error(
                'must specify environment if specifying a config file'
            )
            return False

        if not cfg.load(Path(args.config).resolve()):
            Log.an().error('cannot load config file: %s', args.config)
            return False

        config_dict = cfg.config(args.environment)
        if not config_dict:
            Log.an().error('invalid config environment: %s', args.environment)
            return False

    else:
        # load default config
        cfg.default('database.db')
        config_dict = cfg.config('local')

    # initialize workflow installer object and install apps
    wf_installer = WorkflowInstaller(
        str(Path(args.workflow_path).resolve()),
        git=args.git,
        git_branch=args.git_branch,
        force=args.force,
        app_name=args.name,
        clean=args.clean,
        config=config_dict,
        make_apps=args.make_apps
    )

    if not wf_installer.initialize():
        Log.an().error('cannot initialize workflow installer')
        return False

    if not wf_installer.install_apps():
        Log.an().error('cannot install workflow apps')
        return False

    return True
