# Copyright (c) 2016-present, Ke Mao. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * The names of the contributors may not be used to endorse or
#       promote products derived from this software without specific
#       prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import subprocess as sub
import time

import settings
from util import motifcore_installer
from util import pack_and_deploy


def get_devices():
	""" will also get devices ready
	:return: a list of avaiable devices names, e.g., emulator-5556
	"""
	print "### get_devices..."

	print "### killall adb"
	os.system("kill -9 $(lsof -i:5037 | tail -n +2 | awk '{print $2}')")
	os.system("killall adb")
	print "### adb devices"
	os.system("adb devices")

	ret = []
	p = sub.Popen('adb devices', stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
	output, errors = p.communicate()
	print output
	segs = output.split("\n")
	for seg in segs:
		try:
			status = seg.split("\t")[1].strip()
			if status == "device":
				ret.append(seg.split("\t")[0].strip())
		except:
			pass

	print "### len(ret)", len(ret)
	if len(ret) == 0:
		time.sleep(1)
		return get_devices()

	assert len(ret) > 0
	return ret


def reboot_all_devices():
	"""
	prepare the env of the device
	:return:
	"""
	adb_root()
	for device in get_devices():
		os.system("adb -s " + device + " reboot")

	time.sleep(settings.AVD_BOOT_DELAY)
	adb_root()


def adb_root():
	for device in get_devices():
		os.system("adb -s " + device + " root")


def disable_systemui():
	for device in get_devices():
		os.system("adb -s " + device + " shell service call activity 42 s16 com.android.systemui")


def prepare_motifcore():
	for device in get_devices():
		motifcore_installer.install(settings.WORKING_DIR + "lib/motifcore.jar", settings.WORKING_DIR + "resources/motif", device)


def kill_motifcore(device):
	os.system(
		"adb -s " + device + " shell ps | awk '/com\.android\.commands\.motifcore/ { system(\"adb -s " + device + " shell kill \" $2) }'")


def kill_all_motifcore():
	for device in get_devices():
		os.system(
			"adb -s " + device + " shell ps | awk '/com\.android\.commands\.motifcore/ { system(\"adb -s " + device + " shell kill \" $2) }'")


def pack_and_deploy_aut():
	# instrument the app under test
	pack_and_deploy.main(get_devices())


def clean_device_app(device, package_name):
	os.system("kill -9 $(lsof -i:5037 | tail -n +2 | awk '{print $2}')")
	os.system("killall adb")
	os.system("adb devices")

	print "### kill motifcore ..."
	kill_motifcore(device)
	os.system("adb -s " + device + " shell pm clear " + package_name)
	os.system("adb -s " + device + " shell am force-stop " + package_name)
	os.system("adb -s " + device + " uninstall " + package_name)
	os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
	print "### clean device app finished"


if __name__ == "__main__":
	kill_all_motifcore()
