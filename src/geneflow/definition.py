"""This module contains the GeneFlow Definition class."""

import copy
import pprint

import cerberus
import yaml

from geneflow.log import Log

GF_VERSION = 'v3.0'

WORKFLOW_SCHEMA = {
    'v3.0': {
        'gfVersion': {
            'type': 'string', 'default': GF_VERSION, 'allowed': [GF_VERSION]
        },
        'class': {
            'type': 'string', 'default': 'workflow', 'allowed': ['workflow']
        },
        'workflow_id': {'type': 'string', 'default': ''}, # db artifact
        'name': {'type': 'string', 'required': True, 'coerce': str},
        'description': {'type': 'string', 'required': True, 'coerce': str},
        'git': {'type': 'string', 'required': True, 'coerce': str},
        'version': {'type': 'string', 'required': True, 'coerce': str},
        'author': {'type': 'string', 'default': 'User', 'coerce': str},
        'inputs': {
            'type': 'dict',
            'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
            'default': {},
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'description': {'type': 'string', 'default': '', 'coerce': str},
                    'default': {
                        'anyof': [
                            {'type': 'string'},
                            {'type': 'list', 'schema': {'type': 'string'}}
                        ]
                    },
                    'value': {
                        'anyof': [
                            {'type': 'string'},
                            {'type': 'list', 'schema': {'type': 'string'}}
                        ]
                    }
                }
            }
        },
        'parameters': {
            'type': 'dict',
            'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
            'default': {},
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'description': {'type': 'string', 'default': '', 'coerce': str},
                    'default': {'type': 'string', 'default': '', 'coerce': str},
                    'value': {'type': 'string', 'default': '', 'coerce': str}
                }
            }
        },
        'publish': {
            'type': 'list',
            'schema': {
                'type': 'string',
                'coerce': str
            },
            'default': []
        },
        'apps': {
            'type': 'dict',
            'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
            'required': True,
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'git': {'type': 'string', 'default': '', 'coerce': str},
                    'version': {'type': 'string', 'default': '', 'coerce': str},
                    'inputs': {
                        'type': 'dict',
                        'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
                        'default': {}
                    },
                    'parameters': {
                        'type': 'dict',
                        'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
                        'default': {}
                    },
                    'images': {
                        'type': 'dict',
                        'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
                        'default': {}
                    },
                    'execution': {
                        'type': 'dict',
                        'schema': {
                            'pre': {'type': 'list', 'default': []},
                            'methods': {'type': 'list', 'default': []},
                            'post': {'type': 'list', 'default': []}
                        }
                    }
                }
            }
        },
        'steps': {
            'type': 'dict',
            'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
            'required': True,
            'valueschema': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'step_id': {'type': 'string', 'default': '', 'coerce': str},
                    'name': {'type': 'string', 'default': '', 'coerce': str},
                    'app_id': {'type': 'string', 'default': '', 'coerce': str},
                    'app_name': {
                        'type': 'string',
                        'required': True,
                        'excludes': 'app',
                        'coerce': str
                    },
                    'app': {
                        'type': 'string',
                        'required': True,
                        'excludes': 'app_name',
                        'coerce': str
                    },
                    'depend': {'type': 'list', 'default': []},
                    'number': {'type': 'integer', 'default': 0},
                    'letter': {'type': 'string', 'default': ''},
                    'map': {
                        'type': 'dict',
                        'default': {'uri': '', 'regex': '', 'glob': '*', 'inclusive': False},
                        'schema': {
                            'uri': {'type': 'string', 'default': ''},
                            'inclusive': {'type': 'boolean', 'default': False},
                            'glob': {'type': 'string', 'default': '*'},
                            'regex': {'type': 'string', 'default': ''}
                        }
                    },
                    'template': {
                        'type': 'dict',
                        'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
                        'allow_unknown': True,
                        'schema': {
                            'output': {'type': 'string', 'required': True}
                        }
                    },
                    'publish': {'type': 'boolean', 'default': False},
                    'execution': {
                        'type': 'dict',
                        'default': {'context': 'local', 'method': 'auto', 'parameters': {}},
                        'schema': {
                            'context': {
                                'type': 'string',
                                'default': 'local',
                                'allowed': ['local', 'gridengine', 'slurm']
                            },
                            'method': {
                                'type': 'string',
                                'default': 'auto'
                            },
                            'parameters': {
                                'type': 'dict',
                                'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
                                'allow_unknown': True,
                                'default': {}
                            }
                        }
                    }
                }
            }
        }
    }
}

APP_SCHEMA = {
    'v3.0': {
        'gfVersion': {
            'type': 'string',
            'default': GF_VERSION,
            'allowed': [GF_VERSION]
        },
        'class': {
            'type': 'string',
            'default': 'app',
            'allowed': ['app']
        },
        'app_id': {'type': 'string', 'default': ''},
        'name': {'type': 'string', 'default': '', 'coerce': str},
        'description': {'type': 'string', 'maxlength': 64, 'default': '', 'coerce': str},
        'git': {'type': 'string', 'default': '', 'coerce': str},
        'version': {'type': 'string', 'default': '', 'coerce': str},
        'author': {'type': 'string', 'default': '', 'coerce': str},
        'inputs': {
            'type': 'dict',
            'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
            'default': {},
            'valueschema': {
                'type': 'dict',
                'default': {'description': ''},
                'schema': {
                    'description': {'type': 'string', 'default': '', 'coerce': str},
                    'default': {'type': 'string', 'default': ''},
                    'value': {'type': 'string', 'default': ''},
                    'script_default': {'type': 'string', 'default': ''},
                    'required': {'type': 'boolean', 'default': False},
                    'test_value': {'type': 'string', 'default': ''},
                    'post': {
                        'type': 'list',
                        'default': [],
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'type': {
                                    'type': 'string',
                                    'allowed': ['docker','singularity','shell'],
                                    'default': 'shell'
                                },
                                'image': {'type': 'string', 'coerce': str, 'regex': '[a-zA-Z0-9_]+'},
                                'if': {'type': 'list', 'default': []},
                                'else': {'type': 'list', 'default': []},
                                'run': {'type': 'string', 'coerce': str}
                            }
                        }
                    }
                }
            }
        },
        'parameters': {
            'type': 'dict',
            'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
            'default': {},
            'valueschema': {
                'type': 'dict',
                'default': {'description': ''},
                'schema': {
                    'description': {'type': 'string', 'default': ''},
                    'default': {'type': 'string', 'default': ''},
                    'value': {'type': 'string', 'default': ''},
                    'required': {'type': 'boolean', 'default': False},
                    'test_value': {'type': 'string', 'default': ''},
                    'post': {
                        'type': 'list',
                        'schema': {'type': 'dict'},
                        'nullable': True
                    }
                }
            }
        },
        'images': {
            'type': 'dict',
            'keysrules': {'type': 'string', 'regex': '[a-zA-Z0-9_]+'},
            'default': {},
            'valueschema': {
                'type': 'string',
                'default': '',
                'coerce': str
            }
        },
        'execution': {
            'type': 'dict',
            'schema': {
                'pre': {
                    'type': 'list',
                    'default': [],
                    'schema': {
                        'type': 'dict',
                        'schema': {
                            'type': {
                                'type': 'string',
                                'allowed': ['docker','singularity','shell'],
                                'default': 'shell'
                            },
                            'image': {'type': 'string', 'coerce': str, 'regex': '[a-zA-Z0-9_]+'},
                            'if': {'type': 'list', 'default': []},
                            'else': {'type': 'list', 'default': []},
                            'run': {'type': 'string', 'coerce': str}
                        }
                    }
                },
                'methods': {
                    'type': 'list',
                    'default': [],
                    'schema': {
                        'type': 'dict',
                        'schema': {
                            'name': {'type': 'string', 'coerce': str},
                            'if': {'type': 'list', 'default': []},
                            'commands': {
                                'type': 'list', 
                                'default': [],
                                'schema': {
                                    'type': 'dict',
                                    'schema': {
                                        'type': {
                                            'type': 'string',
                                            'allowed': ['docker','singularity','shell'],
                                            'default': 'shell'
                                        },
                                        'image': {'type': 'string', 'coerce': str, 'regex': '[a-zA-Z0-9_]+'},
                                        'if': {'type': 'list', 'default': []},
                                        'else': {'type': 'list', 'default': []},
                                        'run': {'type': 'string', 'coerce': str}
                                    }
                                }
                            }
                        }
                    }
                },
                'post': {
                    'type': 'list',
                    'default': [],
                    'schema': {
                        'type': 'dict',
                        'schema': {
                            'type': {
                                'type': 'string',
                                'allowed': ['docker','singularity','shell'],
                                'default': 'shell'
                            },
                            'image': {'type': 'string', 'coerce': str, 'regex': '[a-zA-Z0-9_]+'},
                            'if': {'type': 'list', 'default': []},
                            'else': {'type': 'list', 'default': []},
                            'run': {'type': 'string', 'coerce': str}
                        }
                    }
                }
            }
        },
        'implementation': {
            'type': 'dict',
            'required': False,
            'valueschema': {'type': 'dict'}
        }
    }
}

JOB_SCHEMA = {
    'v3.0': {
        'gfVersion': {
            'type': 'string',
            'default': GF_VERSION,
            'allowed': [GF_VERSION]
        },
        'class': {
            'type': 'string',
            'default': 'job',
            'allowed': ['job']
        },
        'job_id': {'type': 'string', 'default': ''},
        'username': {'type': 'string', 'default': 'user'},
        'name': {'type': 'string', 'required': True},
        'workflow_id': {'type': 'string', 'default': ''},
        'workflow_name': {'type': 'string', 'default': ''},
        'output_uri': {'type': 'string', 'required': True},
        'work_uri': {
            'type': 'dict',
            'required': True,
            'valueschema': {'type': 'string'}
        },
        'no_output_hash': {
            'type': 'boolean',
            'default': False,
            'coerce': (lambda s: str(s).lower() in ['true','yes','1'])
        },
        'inputs': {
            'type': 'dict',
            'default': {},
            'valueschema': {
                'anyof': [
                    {'type': 'string'},
                    {'type': 'list', 'schema': {'type': 'string'}}
                ]
            }
        },
        'parameters': {
            'type': 'dict', 'default': {}
        },
        'publish': {
            'type': 'list', 'schema': {'type': 'string'}, 'default': []
        },
        'execution': {
            'type': 'dict',
            'default': {
                'context': {'default': 'local'},
                'method': {'default': 'auto'},
                'parameters': {'default': {}}
            },
            'schema': {
                'context': {
                    'type': 'dict',
                    'default': {'default': 'local'},
                    'allow_unknown': True,
                    'schema': {
                        'default': {
                            'type': 'string',
                            'default': 'local',
                        }
                    },
                    'valueschema': {
                        'type': 'string',
                        'default': 'local',
                        'allowed': [
                            'local',
                            'gridengine',
                            'slurm'
                        ]
                    }
                },
                'method': {
                    'type': 'dict',
                    'default': {'default': 'auto'},
                    'allow_unknown': True,
                    'schema': {
                        'default': {
                            'type': 'string',
                            'default': 'auto'
                        }
                    },
                    'valueschema': {
                        'type': 'string',
                        'default': 'auto'
                    }
                },
                'parameters': {
                    'type': 'dict',
                    'default': {'default': {}},
                    'allow_unknown': True,
                    'schema': {
                        'default': {
                            'type': 'dict',
                            'default': {},
                            'allow_unknown': True
                        }
                    },
                    'valueschema': {
                        'type': 'dict',
                        'default': {},
                        'allow_unknown': True
                    }
                }
            }
        }
    }
}


class Definition:
    """
    GeneFlow Definition class.

    The Definition class is used to load and validate workflow
    definition YAML file and job definition YAML file.
    """

    def __init__(self):
        """Initialize Definition class with default values."""
        self._apps = {}
        self._workflows = {}
        self._jobs = {}


    @classmethod
    def load_yaml(cls, yaml_path):
        """
        Load a multi-doc yaml file.

        Read a multi-doc yaml file and return a list of dicts. Only basic YAML
        validation is performed in this method.

        Args:
            yaml_path: path to multi-doc YAML file.

        Returns:
            List of dicts.

        """
        try:
            with open(yaml_path, 'rU') as yaml_file:
                yaml_data = yaml_file.read()
        except IOError as err:
            Log.an().error(
                'cannot read yaml file: %s [%s]', yaml_path, str(err)
            )
            return False

        try:
            yaml_dict = list(yaml.safe_load_all(yaml_data))
        except yaml.YAMLError as err:
            Log.an().error('invalid yaml: %s [%s]', yaml_path, str(err))
            return False

        return yaml_dict


    def load(self, yaml_path):
        """
        Load and validate GeneFlow definition from a multi-doc YAML file.

        Read a GeneFlow definition file, which can contain apps, workflows,
        and jobs. Loaded docs are appended to the _apps, _workflows, and _jobs
        arrays. Load may be called multiple times. Docs are only added if
        successfully validated.

        Args:
            yaml_path: path to GeneFlow YAML definition file.

        Returns:
            On success: True
            On failure: False.

        """
        # load multi-doc yaml file
        gf_def = self.load_yaml(yaml_path)
        if gf_def is False:
            Log.an().error('cannot load yaml file: %s', yaml_path)
            return False

        # iterate through yaml docs
        for gf_doc in gf_def:
            # class must be specified, either app or workflow
            if 'class' not in gf_doc:
                Log.a().error('unspecified document class')
                return False

            if gf_doc['class'] == 'app':
                if 'apps' in gf_doc:
                    # this is a list of apps
                    for app in gf_doc['apps']:
                        if not self.add_app(app):
                            Log.an().error(
                                'invalid app in definition: %s', yaml_path
                            )
                            return False

                else:
                    # only one app
                    if not self.add_app(gf_doc):
                        Log.an().error(
                            'invalid app in definition: %s', yaml_path
                        )
                        return False

            elif gf_doc['class'] == 'workflow':
                # only one workflow per yaml file allowed
                if not self.add_workflow(gf_doc):
                    Log.an().error(
                        'invalid workflow in definition: %s', yaml_path
                    )
                    return False

            elif gf_doc['class'] == 'job':
                if 'jobs' in gf_doc:
                    # this is a list of jobs
                    for job in gf_doc['jobs']:
                        if not self.add_job(job):
                            Log.an().error(
                                'invalid job in definition: %s', yaml_path
                            )
                            return False

                else:
                    # only one job
                    if not self.add_job(gf_doc):
                        Log.an().error(
                            'invalid job in definition: %s', yaml_path
                        )
                        return False

            else:
                Log.a().error('invalid document class: %s', gf_doc['class'])
                return False

        return True


    @classmethod
    def validate_app(cls, app_def):
        """Validate app definition."""
        validator = cerberus.Validator(APP_SCHEMA[GF_VERSION])
        valid_def = validator.validated(app_def)

        if not valid_def:
            Log.an().error(
                'app validation error:\n%s',
                pprint.pformat(validator.errors)
            )
            return False

        return valid_def


    @classmethod
    def calculate_step_numbering(cls, workflow_dict):
        """
        Calculate step numbering for a workflow.

        Use a topological sort algorithm to calculate step number and validate
        the DAG. Return a workflow dict with populated 'number' and 'letter'
        numbering.

        Args:
            workflow_dict: Dict of workflow to number.

        Returns:
            On success: A workflow dict with step numbers.
            On failure: False.

        """
        # initial step number
        number = 1

        steps = workflow_dict['steps']

        # indicate if step has been traversed
        step_status = {}
        for step in steps:
            step_status[step] = False

        all_done = False
        while not all_done:
            all_done = True
            steps_done = [] # steps to be set to done on next iter
            for step in steps:
                if not step_status[step]:
                    all_done = False # at least one step found
                    # get status of all dependencies, and make sure they're
                    # valid
                    dep_list = []
                    for depend in steps[step]['depend']:
                        if depend not in step_status:
                            Log.an().error(
                                'invalid step dependency: %s', depend
                            )
                            return False

                        dep_list.append(step_status[depend])

                    if not dep_list or all(dep_list):
                        # either no dependencies, or all have been traversed
                        # set step number, allowing ties
                        steps[step]['number'] = number
                        # add step to list of traversed
                        steps_done.append(step)

            if not all_done and not steps_done:
                # if steps remaining, but none have satisfied dependencies
                Log.an().error('cycles found in graph')
                return False

            # mark all steps in steps_done as done, set letter if duplicate
            # step number
            letter = ord('a') # parallel steps labeled starting at 'a'
            for step in sorted(steps_done):
                step_status[step] = True
                if len(steps_done) > 1:
                    steps[step]['letter'] = chr(letter)
                    letter += 1

            # increment step number
            number += 1

        return workflow_dict


    @classmethod
    def validate_workflow(cls, workflow_def):
        """Validate workflow definition."""
        validator = cerberus.Validator(WORKFLOW_SCHEMA[GF_VERSION])
        valid_def = validator.validated(workflow_def)

        if not valid_def:
            Log.an().error(
                'workflow validation error:\n%s',
                pprint.pformat(validator.errors)
            )
            return False

        numbered_def = cls.calculate_step_numbering(copy.deepcopy(valid_def))
        if not numbered_def:
            Log.an().error('invalid workflow step dependencies')
            return False

        for step_name, step in valid_def['steps'].items():
            step['name'] = step_name

        return numbered_def


    @classmethod
    def validate_job(cls, job_def):
        """Validate job definition."""
        validator = cerberus.Validator(JOB_SCHEMA[GF_VERSION])
        valid_def = validator.validated(job_def)

        if not valid_def:
            Log.an().error(
                'job validation error: \n%s',
                pprint.pformat(validator.errors)
            )
            return False

        return valid_def


    def add_app(self, app_def):
        """
        Validate and add app to list.

        Args:
            app_def: dict of app definition.

        Returns:
            On success: True.
            On failure: False.

        """
        valid_def = self.validate_app(app_def)
        if not valid_def:
            Log.an().error('invalid app:\n%s', yaml.dump(app_def))
            return False

        if valid_def['name'] in self._apps:
            Log.an().error('duplicate app name: %s', valid_def['name'])
            return False

        self._apps[valid_def['name']] = valid_def

        return True


    def add_workflow(self, workflow_def):
        """
        Validate and add workflow to list.

        Args:
            workflow_def: dict of workflow definition.

        Returns:
            On success: True.
            On failure: False.

        """
        valid_def = self.validate_workflow(workflow_def)
        if not valid_def:
            Log.an().error('invalid workflow:\n%s', yaml.dump(workflow_def))
            return False

        if valid_def['name'] in self._workflows:
            Log.an().error('duplicate workflow name: %s', valid_def['name'])
            return False

        self._workflows[valid_def['name']] = valid_def

        return True


    def add_job(self, job_def):
        """
        Validate and add job to list.

        Args:
            job_def: dict of job definition.

        Returns:
            On success: True.
            On failure: False.

        """
        valid_def = self.validate_job(job_def)
        if not valid_def:
            Log.an().error('invalid job:\n%s', yaml.dump(job_def))
            return False

        if valid_def['name'] in self._jobs:
            Log.an().error('duplicate job name: %s', valid_def['name'])
            return False

        self._jobs[valid_def['name']] = valid_def

        return True


    def apps(self, name=None):
        """
        Get app dicts.

        Return either all apps (name=None), or a specific app from dict. If
        dict key doesn't exist, an empty dict is returned and an error is
        logged.

        Args:
            name: name of app to return, None (default) indicates all apps.

        Returns:
            Dict of apps.

        """
        if name is None:
            return self._apps

        if name not in self._apps:
            Log.an().error('app not found: %s', name)
            return {}

        return self._apps[name]


    def workflows(self, name=None):
        """
        Get workflow dicts.

        Return either all workflows (name=None), or a specific workflow from
        dict. If dict key doesn't exist, an empty dict is returned and an error
        is logged.

        Args:
            name: name of workflow to return, None (default) indicates all
            workflows.

        Returns:
            Dict of workflows.

        """
        if name is None:
            return self._workflows

        if name not in self._workflows:
            Log.an().error('workflow not found: %s', name)
            return {}

        return self._workflows[name]


    def jobs(self, name=None):
        """
        Get job dicts.

        Return either all jobs (name=None), or a specific job from dict. If
        dict key doesn't exist, an empty dict is returned and an error is
        logged.

        Args:
            name: name of job to return, None (default) indicates all
            jobs.

        Returns:
            Dict of jobs.

        """
        if name is None:
            return self._jobs

        if name not in self._jobs:
            Log.an().error('job not found: %s', name)
            return {}

        return self._jobs[name]
