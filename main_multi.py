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
import datetime

import settings

if __name__ == "__main__":
	"""
	For batch processing APKs. One hour per APK
	All intermediate output are saved under the instrumented app folder
	"""
	start = 1
	for i in range(start, settings.REPEATED_RUNS + start):

		instrumented_app_dirs = []
		apk_path = settings.APK_DIR

		ith_apk = 0

		for dir in os.listdir(apk_path):
			dir_path = apk_path + dir
			if os.path.isdir(dir_path):
				target_dir = settings.REPEATED_RESULTS_DIR + "/" + str(i) + "/" + dir_path.split("/")[-1]
				if ith_apk >= settings.APK_OFFSET and (not os.path.exists(target_dir)):
					instrumented_app_dirs.append(dir_path)
				ith_apk += 1

		print "Will work on apps:", instrumented_app_dirs

		for app_dir in instrumented_app_dirs:
			os.system(settings.TIMEOUT_CMD + " 3600 python main.py " + app_dir)
			print "3600 timeout. Will work on next app ..."

			os.system("touch " + app_dir + "/intermediate/finished_at_" + datetime.datetime.now().strftime(
				"%Y_%m_%d_%H_%M_%S"))
			time.sleep(10)

			target_dir = settings.REPEATED_RESULTS_DIR + "/" + str(i) + "/" + app_dir.split("/")[-1]
			os.system("mkdir -p " + target_dir)
			os.system("cp -r " + app_dir + "/intermediate " + target_dir)
			os.system("cp -r " + app_dir + "/crashes " + target_dir)
			os.system("cp -r " + app_dir + "/coverages " + target_dir)

	print "### All Done."