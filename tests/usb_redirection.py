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

import os
import logging
from virttest import utils_net, utils_spice, remote


def _create_usb_storage(vm, storage_file, size_of_storage):
    """
    Method created USB storage with proper size and creates there file
    with content.
    USB device is created on host then is with monitor command attached to guest


    @param session: VM's session
    @param storage_file: emulated USB file
    @param size_of_storage: size of storage in MB
    """

    os.system("rm -rf %s" % storage_file)
    logging.debug("Creating device %s" % storage_file)
    os.system('dd if=/dev/zero of=%s bs=%sM count=1' % (storage_file,
                                                size_of_storage))
    logging.debug("Creating filesystem ext3 on %s" % storage_file)
    os.system("mkfs.ext3 -F -L test -q %s " % storage_file)

    vm.monitor.cmd("usb_add disk:%s" % storage_file)
#enddef

def _mount_usb_storage(session):
    logging.debug("Creating mount point")
    session.cmd("mkdir /mnt/usb")

    logging.debug("Mounting usb")
    session.cmd("mount -o loop=/dev/loop0 /tmp/usb.img /mnt/usb")

    logging.debug("Copy text to usb")
    session.cmd("echo 'This is the test' > /mnt/usb/test")
#enddef


def create_random_file(session, path, size):
    """
    Creates file with path size with random data.
    Returns md5hash of this file.

    @param session: VM session
    @param path: path to file
    @param size: size of file

    @return md5hash of file
    """
    session.cmd("dd if=/dev/random of=%s bs=%s count=1" % (path, size))
    session.cmd("md5sum %s" % path)

def run_usb_redirection(test, params, env):
    """
    Test for USB connection
    Storage for USB device is created in qemu_vm.py. Then is
    guest VM started with USB redirection options and configuration
    files. Client VM is started with emulated USB device.

    This test copy data from client to guest in both ways.

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
    utils_spice.launch_startx(guest_vm)
    utils_spice.wait_timeout(10)
    #create file on guest
    guest_session.cmd("dd if=/dev/random of=%s bs=%s count=1" % ("/tmp/test.file", 4))
    md5sum_guest = guest_session.cmd("md5sum %s" % "/tmp/test.file")
    logging.info("MD5SUM on guest: %s" % md5sum_guest)
    #copy file on USB
    guest_session.cmd("cp %s %s" % ("/tmp/test.file", "/media/test/test.file"))
    md5sum_guest_usb = guest_session.cmd("md5sum %s" % "/media/test/test.file")
    logging.info("MD5SUM on guest USB: %s" % md5sum_guest_usb)
    #disconnect USB (kill remote-viewer)
    rv_id = guest_session.cmd("pgrep remote-viewer")
    guest_session.cmd("pkill %s" % rv_id)
    #check md5sum on client USB
    md5sum_client_usb = client_session.cmd("md5sum %s" % "/media/test/test.file")
    logging.info("MD5SUM on client USB: %s" % md5sum_client_usb)
    #copy file to client
    client_session.cmd("cp %s %s" % ("/media/test/test.file", "/tmp/test.file"))
    #check md5sum 
    md5sum_client = client_session.cmd("md5sum %s" % "/tmp/test.file")
    logging.info("MD5SUM on client: %s" % md5sum_client)
    
    