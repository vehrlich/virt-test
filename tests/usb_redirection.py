"""
usb_insert.py - tests USB connection, file transfer
"""
import os
import logging

def _create_usb_storage(session, size_of_storage):
    """
    Method created USB storage with proper size and creates there file
    with content.
    
    @param session: VM's session 
    @param size_of_storage: size of storage in MB 
    """
    #clean possible image and mount point from last use
    try:
        session.cmd("mount | grep /mnt/usb")
    except:
        pass
    else:
        logging.debug("Umount /mnt/usb")
        session.cmd("umount /mnt/usb")
        
    try:
        session.cmd("ls /mnt/usb")
    except:
        pass
    else:
        logging.debug("Remove mount point")
        session.cmd("rm -rf /mnt/usb")

    try:
        session.cmd("ls /tmp/usb.img")
    except:
        pass
    else:
        logging.debug("Remove image")
        session.cmd("rm -rf /tmp/usb.img")
    
    logging.debug("Creating device /tmp/usb.img")
    session.cmd("dd if=/dev/zero of=/tmp/usb.img bs=%sM count=1" % size_of_storage)

    logging.debug("Creating filesystem ext3 on /tmp/usb.img")
    session.cmd("mkfs.ext3 -F -L test -q /tmp/usb.img")
#enddef

def _mount_usb_storage(session):
    logging.debug("Creating mount point")
    session.cmd("mkdir /mnt/usb")

    logging.debug("Mounting usb")
    session.cmd("mount -o loop=/dev/loop0 /tmp/usb.img /mnt/usb")

    logging.debug("Copy text to usb")
    session.cmd("echo 'This is the test' > /mnt/usb/test")
#enddef

def run_usb_redirection(test, params, env):
    """
    Test for USB connection
    
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

    #create usb storage
    #_create_usb_storage(client_session, params.get("storage_size", 1))
    #_mount_usb_storage(client_session)