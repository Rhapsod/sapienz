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


import subprocess
import os


def handle(device, apk_dir, script_path, gen, pop, index, unique_crashes):
	"""
	:param device:
	:param apk_dir:
	:param script_path:
	:param gen_str: string, "init" is caused when init,
		"0" is caused when evaluate the init population
	:return: True if it is a real crash
	"""

	p = subprocess.Popen("adb -s " + device + " shell ls /mnt/sdcard/bugreport.crash", stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE, shell=True)
	output, errors = p.communicate()
	if output.find("No such file or directory") != -1:
		# no crash
		pass
	else:
		# save the crash report
		os.system("adb -s " + device + " pull /mnt/sdcard/bugreport.crash " + apk_dir + "/")
		# filter duplicate crashes
		with open(apk_dir + "/bugreport.crash") as bug_report_file:
			content = ""
			for line_no, line in enumerate(bug_report_file):
				if line_no == 0:
					# should not caused by android itself
					if line.startswith("// CRASH: com.android."):
						os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
						return False
					continue
				content += line
			if content in unique_crashes:
				os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
				return False
			else:
				unique_crashes.add(content)

		# ts = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.%f")[:-3]
		os.system("mv " + apk_dir + "/bugreport.crash " + apk_dir + "/crashes/" + "bugreport." + str(gen) + "." + str(
			pop) + "." + str(index))
		# save the script, indicate its ith gen
		os.system("cp " + script_path + " " + apk_dir + "/crashes/" + "script." + str(gen) + "." + str(pop) + "." + str(
			index))
		print "### Caught a crash."
		os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
		return True

	os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
	return False
