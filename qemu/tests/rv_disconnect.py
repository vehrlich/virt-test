"""
rv_disconnect.py - Disconnects remote-viewer by kiling it.

"""
import logging
import os
from autotest.client.shared import error
from virttest import utils_spice


def run_rv_disconnect(test, params, env):
    """
    Test kills application. Application is given by name kill_app_name in
    params.
    It has to be defined if application is on guest or client with parameter
    kill_on_vms which should contain name(s) of vm(s) (separated with ',')

    :param test: KVM test object.
    :param params: Dictionary with the test parameters.
    :param env: Dictionary with test environment.
    """
    kill_on_vms = params.get("kill_on_vms", "")
    vms = kill_on_vms.split(',')
    app_name = params.get("rv_binary", None)
    logging.debug("vms %s", vms)
    if not vms:
        raise error.TestFail("Kill app test launched without any VM parameter")
    else:
        for vm in vms:
            logging.debug("vm %s", vm)
            if params.has_key(vm):
                utils_spice.kill_app(vm, app_name, params, env)
