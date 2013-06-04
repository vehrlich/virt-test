install
KVM_TEST_MEDIUM
text
reboot
lang en_US.UTF-8
keyboard us
key --skip
network --bootproto dhcp
rootpw --plaintext 123456
user --name=test --password=123456 --plaintext
firewall --enabled --ssh
selinux --enforcing
timezone --utc America/New_York
firstboot --disable
bootloader --location=mbr --append="console=tty0 console=ttyS0,115200"
zerombr
xconfig --startxonboot
clearpart --all --initlabel
autopart
poweroff
KVM_TEST_LOGGING

%packages
@base
@core
@development
@additional-devel
@debugging-tools
@network-tools
@x11
@basic-desktop
@fonts
@Smart Card Support
NetworkManager
ntpdate
watchdog
coreutils
usbutils
spice-xpi
virt-viewer
spice-vdagent
usbredir
SDL
totem
%end

%post --interpreter /usr/bin/python
import os
os.system('grubby --remove-args="rhgb quiet" --update-kernel=$(grubby --default-kernel)')
os.system('dhclient')
os.system('chkconfig sshd on')
os.system('iptables -F')
os.system('echo 0 > /selinux/enforce')
os.system('echo Post set up finished > /dev/ttyS0')
os.system('echo Post set up finished > /dev/hvc0')

f = open('/etc/gdm/custom.conf','w')
f.write('[daemon]\n'
        'AutomaticLogin=test\n'
        'AutomaticLoginEnable=True\n')
f.close()
f = open('/etc/sudoers','a')
f.write('test ALL = NOPASSWD: /sbin/shutdown -r now,/sbin/shutdown -h now\n')
f.close()
f = open('/home/test/.bashrc','a')
f.write('alias shutdown=\'sudo shutdown\'\n')
f.close()
f = open('/etc/rc.modules','w')
f.write('modprobe snd-aloop\n'
        'modprobe snd-pcm-oss\n'
        'modprobe snd-mixer-oss\n'
        'modprobe snd-seq-oss\n')
f.close()
os.system('chmod +x /etc/rc.modules')
%end
