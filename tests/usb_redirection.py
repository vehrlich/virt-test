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

This means there is no way how to simulate USB redirection in RHEL 6.3. In
RHEL6.4 is possible to use remote-viewer option. In future it will be more easy
with qemu-kvm monitor command
"""

import logging
from virttest import utils_misc, utils_spice
from autotest.client.shared import utils, error


def run_usb_redirection(test, params, env):
    """
    Test for USB connection
    Storage for USB device is created in qemu_vm.py. Then is
    guest VM started with USB redirection options and configuration
    files. Client VM is started with emulated USB device.

    This test copy data from guest to client through USB.

    Test expects remote-viewer running (rv_connect)

    #TODO paths are hardcoded this will be problem with Windows USB redir. Make
    #it more sophisticated.

    @param test: KVM test object.
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """
    #prepare guest and client sessions
    guest_vm = env.get_vm(params["guest_vm"])
    guest_vm.verify_alive()
    guest_session = guest_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)))

    client_vm = env.get_vm(params["client_vm"])
    client_vm.verify_alive()
    client_session = client_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)))

    client_root_session = client_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)),
            username="root", password="123456")

    guest_root_session = guest_vm.wait_for_login(
            timeout=int(params.get("login_timeout", 360)),
            username="root", password="123456")

    #create file on guest
    guest_session.cmd("dd if=/dev/urandom of=%s%s bs=%s count=1" % (
                      params["file_tmp_path"], 
                       params["usb_file"],
                       params["file_size"]
                      ), timeout=120)
    #get md5 hash
    md5sum_guest = guest_session.cmd("md5sum %s%s | cut -f1 -d\" \"" % (
                                      params["file_tmp_path"], 
                                      params["usb_file"]
                                     ))

    logging.info("MD5SUM on guest: %s" % md5sum_guest)
    #USB was mounted by root when tested this test. This prevents right issue
    guest_root_session.cmd("chmod 777 %s" % params["file_path"])
    #copy file from guest to USB(USB is mounted automaticaly to /media )
    if params.get("migrate", "no") == "yes":
        copy_background = utils.InterruptedThread(
                            guest_session.cmd, ("cp %s%s %s%s" % (
                            params["file_tmp_path"], 
                            params["usb_file"],
                            params["file_path"], 
                            params["usb_file"]),), 
                            kwargs={'timeout' : 300})
        
    
        copy_background.start()
        try:
            while copy_background.isAlive():
                guest_vm.migrate()
        except Exception:
            # If something bad happened in the main thread, ignore
            # exceptions raised in the background thread
            copy_background.join(suppress_exception=True)
            raise
        else:
            copy_background.join()
    else:
        guest_session.cmd("cp %s%s %s%s &" % (
                                              params["file_tmp_path"], 
                                              params["usb_file"],
                                              params["file_path"], 
                                              params["usb_file"]
                                              ), timeout=300)

    md5sum_guest_usb = guest_session.cmd("md5sum %s%s | cut -f1 -d\" \"" % (
                                        params["file_path"], 
                                        params["usb_file"]
                                        ))
    logging.info("MD5SUM on guest USB: %s" % md5sum_guest_usb)
    #disconnect USB
    guest_root_session.cmd("umount %s" % params["file_path"], timeout=120)
    #USB hold by guest is freed after VM shutdown (maybe bug? Should not be closing
    #client enough?)
    guest_vm.destroy()
    client_session.cmd("pkill remote-viewer")
    utils_spice.wait_timeout(10)
    #check md5sum on client USB
    md5sum_client_usb = client_session.cmd("md5sum %s%s | cut -f1 -d\" \"" % (
                                      params["file_path"], 
                                      params["usb_file"]
                                     ))

    logging.info("MD5SUM on client USB: %s" % md5sum_client_usb)
    #copy file to client
    client_session.cmd("cp %s%s %s%s" % (
                                          params["file_path"], 
                                          params["usb_file"],
                                          params["file_tmp_path"], 
                                          params["usb_file"]
                                          ))
    #check md5sum
    md5sum_client = client_session.cmd("md5sum %s%s | cut -f1 -d\" \"" % (
                                      params["file_path"], 
                                      params["usb_file"]
                                     ))
    logging.info("MD5SUM on client: %s", md5sum_client)

    if md5sum_guest == md5sum_guest_usb == md5sum_client_usb ==  md5sum_client:
        logging.info("MD5SUM check PASS")
        return True
    else:
        raise error.TestFail("MD5SUM check FAILED\n%s\n%s\n%s\n%s",
                             md5sum_guest,
                             md5sum_guest_usb,
                             md5sum_client_usb,
                             md5sum_client)

    client_session.close()
    guest_session.close()
