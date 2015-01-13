"""
Starter fabfile for deploying the open cultuurdata api.

Change all the things marked CHANGEME. Other things can be left at their
defaults if you are happy with the default layout.
"""

import os
import posixpath
from pprint import pprint

from fabric.api import run, local, env, settings, cd, task, put, execute
from fabric.contrib.files import exists
from fabric.operations import _prefix_commands, _prefix_env_vars, require
#from fabric.decorators import runs_once
#from fabric.context_managers import cd, lcd, settings, hide

# CHANGEME
STAGES = {
    'test': {
        #  'hosts': ['breyten@api.opencultuurdata.nl'],
        'hosts': ['api.opencultuurdata.nl'],
        'code_dir': '/home/breyten/open-cultuur-data-test',
        'code_branch': 'dev',
        'project_dir': '/home/breyten/open-cultuur-data-test',
        'virtualenv': '/home/breyten/open-cultuur-data-test/.virtualenv',
        'code_repo': 'git@github.com:openstate/open-cultuur-data.git',
        'docs_built_dir': '/home/breyten/open-cultuur-data-test/docs-built'
    },
    'production': {
        'hosts': ['breyten@api.opencultuurdata.nl'],
        'code_dir': '/home/breyten/open-cultuur-data',
        'code_branch': 'master',
        'project_dir': '/home/breyten/open-cultuur-data',
        'virtualenv': '/home/breyten/open-cultuur-data/.virtualenv',
        'code_repo': 'git@github.com:openstate/open-cultuur-data.git',
        'docs_built_dir': '/home/breyten/open-cultuur-data-test/docs-built'
    }
}

# Python version
PYTHON_BIN = "python2.7"
PYTHON_PREFIX = ""  # e.g. /usr/local  Use "" for automatic
PYTHON_FULL_PATH = "%s/bin/%s" % (
    PYTHON_PREFIX, PYTHON_BIN) if PYTHON_PREFIX else PYTHON_BIN


def virtualenv(venv_dir):
    """
    Context manager that establishes a virtualenv to use.
    """
    return settings(venv=venv_dir)


def run_venv(command, **kwargs):
    """
    Runs a command in a virtualenv (which has been specified using
    the virtualenv context manager
    """
    run("source %s/bin/activate" % env.virtualenv + " && " + command, **kwargs)


def install_dependencies():
    ensure_virtualenv()
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            run_venv("pip install -r requirements.txt")
            backend_local_file = "ocd_backend/local_settings_%s.py" % (
                env.stage)
            frontend_local_file = "ocd_frontend/local_settings_%s.py" % (
                env.stage)
            if os.path.exists(backend_local_file):
                put(backend_local_file, os.path.join(
                    env.project_dir, 'ocd_backend/local_settings.py'))
            if os.path.exists(frontend_local_file):
                put(frontend_local_file, os.path.join(
                    env.project_dir, 'ocd_frontend/local_settings.py'))


def ensure_virtualenv():
    if exists(env.virtualenv):
        return

    with cd(env.code_dir):
        run("virtualenv --no-site-packages --python=%s %s" %
            (PYTHON_BIN, env.virtualenv))
        run("echo %s > %s/lib/%s/site-packages/projectsource.pth" %
            (env.project_dir, env.virtualenv, PYTHON_BIN))


def ensure_src_dir():
    if not exists(env.code_dir):
        run("mkdir -p %s" % env.code_dir)
    with cd(env.code_dir):
        if not exists(posixpath.join(env.code_dir, '.git')):
            run('git clone --branch=%s %s .' % (
                env.code_branch, env.code_repo,))


def push_sources():
    """
    Push source code to server
    """
    ensure_src_dir()
    local('git checkout %s && git push origin %s' % (
        env.code_branch, env.code_branch,))
    with cd(env.code_dir):
        run('git pull origin %s' % env.code_branch)


@task
def build_documentation():
    ensure_virtualenv()
    with virtualenv(env.virtualenv):
        with cd(env.code_dir):
            run('sphinx-build docs %s' % env.docs_built_dir)


@task
def run_tests():
    """ Runs the Django test suite as is.  """
    local("./run_tests.sh")


@task
def version():
    """ Show last commit to the deployed repo. """
    with cd(env.code_dir):
        run('git log -1')


@task
def uname():
    """ Prints information about the host. """
    run("uname -a")


@task
def webserver_restart():
    """
    Restarts the webserver that is running the Django instance
    """
    pass


def restart():
    """ Restart the wsgi process """
    with cd(env.code_dir):
        run("touch %s/uwsgi.txt" % env.code_dir)


@task
def first_deployment_mode():
    """
    Use before first deployment to switch on fake south migrations.
    """
    env.initial_deploy = True


@task
def sshagent_run(cmd):
    """
    Helper function.
    Runs a command with SSH agent forwarding enabled.

    Note:: Fabric (and paramiko) can't forward your SSH agent.
    This helper uses your system's ssh to do so.
    """
    # Handle context manager modifications
    wrapped_cmd = _prefix_commands(_prefix_env_vars(cmd), 'remote')
    try:
        host, port = env.host_string.split(':')
        return local(
            "ssh -p %s -A %s@%s '%s'" % (port, env.user, host, wrapped_cmd)
        )
    except ValueError:
        return local(
            "ssh -A %s@%s '%s'" % (env.user, env.host_string, wrapped_cmd)
        )


def stage_set(stage_name='test'):
    env.stage = stage_name
    for option, value in STAGES[env.stage].items():
        setattr(env, option, value)


@task
def production():
    stage_set('production')


@task
def test():
    stage_set('test')


@task
def deploy():
    """
    Deploy the project.
    """

    require('stage', provided_by=(test, production,))

    push_sources()
    install_dependencies()
    build_documentation()
    webserver_restart()
