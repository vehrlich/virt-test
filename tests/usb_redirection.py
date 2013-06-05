"""
usb_redirection.py - tests USB connection, file transfer

There are two ways how to simulate USB plugin and redirection.

One is with remote-viewer option --spice-usbredir-redirect-on-connect
This option is not present in virt-viewer 0.5.2-4 in RHEL 6.3.
But is used in virt-viewer 0.5.2-18 in RHEL 6.4. 

Second is use qemu monitor command and add USB device after remote-viewer 
connection.
Unfortunately this command is not present in qemu-kvm 0.1.12 which is used in 
RHEL 6.4.

This means there is no way how to simulate USB redirection in RHEL 6.3. 
In RHEL6.4 is possible to use remote-viewer option.
In future it will be more easy with qemu-kvm monitor command
"""

import logging
from virttest import utils_spice

def check_usb_policy(vm, params):
    """
    Check USB policy in polkit file
    """    
    logging.info("Checking USB policy")
    file = '/usr/share/polkit-1/actions/org.spice-space.lowlevelusbaccess.policy'
    cmd = "grep \"<allow_all>yes\" " + file + " & > /dev/null"
    logging.info("CMD : %s" % cmd)
    client_root_session = vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)),
            username="root", password="123456")
    usb_policy = client_root_session.cmd_status(cmd)
    logging.info("Policy %s" % usb_policy)
    return usb_policy

def add_usb_policy(vm, params):
    """
    Add USB policy to policykit file
    """
    logging.info("Adding USB policy")
    file = "/usr/share/polkit-1/actions/org.spice-space.lowlevelusbaccess.policy"
    client_root_session = vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)),
            username="root", password="123456")
    #get line number of old definition
    cmd = "grep -n \"<allow_active>\" %s | cut -d : -f 1" % file
    line_number = client_root_session.cmd_output(cmd)
    
    logging.info(line_number)
    
    #put new definition after this line number
    #cmd = "(echo '%sa'; echo '<allow_all>yes</allow_all>'; echo 'wq') | ed -s %s" % (line_number, file)
    #client_root_session.cmd(cmd)


def run_usb_redirection(test, params, env):
    """
    Test for USB connection
    Storage for USB device is created in qemu_vm.py. Then is
    guest VM started with USB redirection options and configuration
    files. Client VM is started with emulated USB device.

    This test copy data from client to guest in both ways.
    
    #TODO paths are hardcoded this will be problem with Windows USB redir. Make
    #it more sophisticated.

    @param test: KVM test object.
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """
    guest_vm = env.get_vm(params["guest_vm"])
    guest_vm.verify_alive()
    guest_session = guest_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)))

    client_vm = env.get_vm(params["client_vm"])
    client_vm.verify_alive()
    client_session = client_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)))
    
    if not check_usb_policy(client_vm, params):
        logging.info("No USB policy")
        add_usb_policy(client_vm, params)
    else:
        logging.info("USB policy OK")

    
    #create file on guest
    guest_session.cmd("dd if=/dev/random of=%s bs=%s count=1" %
                      ("/tmp/test.file", "4M"))
    md5sum_guest = guest_session.cmd("md5sum /tmp/test.file")
    logging.info("MD5SUM on guest: %s" % md5sum_guest)
    #copy file from guest to USB
    guest_session.cmd("cp %s %s" % ("/tmp/test.file", "/media/test/test.file"))
    md5sum_guest_usb = guest_session.cmd("md5sum /media/test/test.file")
    logging.info("MD5SUM on guest USB: %s" % md5sum_guest_usb)
    #disconnect USB (kill remote-viewer)
    guest_session.cmd("umount /media/test")
    client_session.cmd("pkill remote-viewer")
    utils_spice.wait_timeout(10)
    #check md5sum on client USB
    md5sum_client_usb = client_session.cmd("md5sum /media/test/test.file")
    logging.info("MD5SUM on client USB: %s" % md5sum_client_usb)
    #copy file to client
    client_session.cmd("cp %s %s" % ("/media/test/test.file", "/tmp/test.file"))
    #check md5sum 
    md5sum_client = client_session.cmd("md5sum /tmp/test.file")
    logging.info("MD5SUM on client: %s", md5sum_client)
    
    if md5sum_guest == md5sum_guest_usb ==  md5sum_client_usb ==  md5sum_client:
        logging.info("MD5SUM check PASS")
        return True
    else:
        logging.info("MD5SUM check FAILED")
        return False
