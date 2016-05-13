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
import time

import subprocess as sub

import settings
from util import motifcore_installer
from util import pack_and_deploy


def get_devices():
	""" will also get devices ready
	:return: a list of avaiable devices names, e.g., emulator-5556
	"""
	ret = []
	p = sub.Popen('adb devices', stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
	output, errors = p.communicate()
	print output
	segs = output.split("\n")
	for seg in segs:
		device = seg.split("\t")[0].strip()
		if seg.startswith("emulator-"):
			p = sub.Popen('adb -s ' + device + ' shell getprop init.svc.bootanim', stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
			output, errors = p.communicate()
			if output.strip() != "stopped":
				time.sleep(10)
				print "waiting for the emulator:", device
				return get_devices()
			else:
				ret.append(device)

	assert len(ret) > 0

	return ret


def boot_devices():
	"""
	prepare the env of the device
	:return:
	"""
	for i in range(0, settings.DEVICE_NUM):
		device_name = settings.AVD_SERIES + str(i)
		print "Booting Device:", device_name
		time.sleep(0.3)
		if settings.HEADLESS:
			sub.Popen('emulator -avd ' + device_name + " -wipe-data -no-audio -no-window",
					  stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
		else:
			sub.Popen('emulator -avd ' + device_name + " -wipe-data -no-audio",
					  stdout=sub.PIPE, stderr=sub.PIPE, shell=True)

	print "Waiting", settings.AVD_BOOT_DELAY, "seconds"
	time.sleep(settings.AVD_BOOT_DELAY)


def clean_sdcard():
	for device in get_devices():
		os.system("adb -s " + device + " shell mount -o rw,remount rootfs /")
		os.system("adb -s " + device + " shell chmod 777 /mnt/sdcard")

		os.system("adb -s " + device + " shell rm -rf /mnt/sdcard/*")


def prepare_motifcore():
	for device in get_devices():
		motifcore_installer.install(settings.WORKING_DIR + "lib/motifcore.jar", settings.WORKING_DIR + "resources/motifcore", device)


def pack_and_deploy_aut():
	# instrument the app under test
	pack_and_deploy.main(get_devices())


def destory_devices():
	# for device in get_devices():
	# 	os.system("adb -s " + device + " emu kill")
	# do force kill
	os.system("kill -9  $(ps aux | grep 'emulator' | awk '{print $2}')")


if __name__ == "__main__":
	destory_devices()