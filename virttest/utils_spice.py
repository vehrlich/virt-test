"""
Common spice test utility functions.

"""
import logging, time
from autotest.client.shared import error
from aexpect import ShellCmdError


def wait_timeout(timeout=10):
    """
    time.sleep(timeout) + logging.debug(timeout)

    @param timeout=10
    """
    logging.debug("Waiting (timeout=%ss)", timeout)
    time.sleep(timeout)

def launch_gnome_session(vm_session):
    """
    Launches gnome session inside VM session
    @param vm_session - vm.wait_fo_login()

    metacity ensures that newly raised window will be active
    (remote-viewer auth dialog)
    which is not done by default in pure Xorg
    """
    cmd = "nohup gnome-session --display=:0.0 &> /dev/null &"
    return vm_session.cmd(cmd)

def launch_xorg(vm_session):
    """
    Launches Xorg inside vm_session on background
    @param vm_session - vm.wait_for_login()
    """
    cmd = "Xorg"
    killall(vm_session, cmd)
    wait_timeout() # Wait for Xorg to exit
    cmd = "nohup " + cmd + " &> /dev/null &"
    return vm_session.cmd(cmd)

def killall(vm_session, pth):
    """
    calls killall execname
    @params vm_session
    @params pth - path or execname
    """
    execname = pth.split(os.path.sep)[-1]
    vm_session.cmd("killall %s &> /dev/null" % execname, ok_status=[0, 1])

def start_vdagent(guest_session, test_timeout):
    """
    Sending commands to start the spice-vdagentd service

    @param guest_session: ssh session of the VM
    @param test_timeout: timeout time for the cmds
    """
    cmd = "service spice-vdagentd start"
    try:
        guest_session.cmd(cmd, print_func=logging.info,
                                   timeout=test_timeout)
    except:
        raise error.TestFail("Guest Vdagent Daemon Start failed")

    logging.debug("------------ End of guest checking for Spice Vdagent"
                  " Daemon ------------")
    wait_timeout(3)


def restart_vdagent(guest_session, test_timeout):
    """
    Sending commands to restart the spice-vdagentd service

    @param guest_session: ssh session of the VM
    @param test_timeout: timeout time for the cmds
    """
    cmd = "service spice-vdagentd restart"
    try:
        guest_session.cmd(cmd, print_func=logging.info,
                                   timeout=test_timeout)
    except ShellCmdError:
        raise error.TestFail("Couldn't restart spice vdagent process")
    except:
        raise error.TestFail("Guest Vdagent Daemon Check failed")

    logging.debug("------------ End of Spice Vdagent"
                     " Daemon  Restart ------------")
    wait_timeout(3)


def stop_vdagent(guest_session, test_timeout):
    """
    Sending commands to stop the spice-vdagentd service

    @param guest_session: ssh session of the VM
    @param test_timeout: timeout time for the cmds
    """
    cmd = "service spice-vdagentd stop"
    try:
        guest_session.cmd(cmd, print_func=logging.info,
                                   timeout=test_timeout)
    except ShellCmdError:
        raise error.TestFail("Couldn't turn off spice vdagent process")
    except:
        raise error.TestFail("Guest Vdagent Daemon Check failed")

    logging.debug("------------ End of guest checking for Spice Vdagent"
                  " Daemon ------------")
    wait_timeout(3)


def verify_vdagent(guest_session, test_timeout):
    """
    Verifying vdagent is installed on a VM

    @param guest_session: ssh session of the VM
    @param test_timeout: timeout time for the cmds
    """
    cmd = "rpm -qa | grep spice-vdagent"

    try:
        guest_session.cmd(cmd, print_func=logging.info, timeout=test_timeout)
    finally:
        logging.debug("----------- End of guest check to see if vdagent package"
                     " is available ------------")
    wait_timeout(3)


def verify_virtio(guest_session, test_timeout):
    """
    Verify Virtio linux driver is properly loaded.

    @param guest_session: ssh session of the VM
    @param test_timeout: timeout time for the cmds
    """
    #cmd = "lsmod | grep virtio_console"
    cmd = "ls /dev/virtio-ports/"
    try:
        guest_session.cmd(cmd, print_func=logging.info, timeout=test_timeout)
    finally:
        logging.debug("------------ End of guest check of the Virtio-Serial"
                     " Driver------------")
    wait_timeout(3)
