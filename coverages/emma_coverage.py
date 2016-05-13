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
import datetime
import time
import subprocess
import threading

from lxml import html
from bs4 import UnicodeDammit

import settings
from crashes import crash_handler


class Command(object):
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None

	def run(self, timeout):
		def target():
			print '... Evaluate Script Thread started'
			self.process = subprocess.Popen(self.cmd, shell=True)
			self.process.communicate()
			print '... Evaluate Script Thread finished'

		thread = threading.Thread(target=target)
		thread.start()

		thread.join(timeout)
		if thread.is_alive():
			print 'Terminating process'
			self.process.terminate()
			thread.join()
		print self.process.returncode


def extract_coverage(path):
	with open(path, 'rb') as file:
		content = file.read()
		doc = UnicodeDammit(content, is_html=True)

	parser = html.HTMLParser(encoding=doc.original_encoding)
	root = html.document_fromstring(content, parser=parser)
	return root.xpath('/html/body/table[2]/tr[2]/td[5]/text()')[0].strip()


# return accumulative coverage and average length
def get_suite_coverage(scripts, device, apk_dir, package_name, gen, pop):
	unique_crashes = set()

	# clean states
	os.system("adb -s " + device + " shell am force-stop " + package_name)
	os.system("adb -s " + device + " shell pm clear " + package_name)
	os.system("adb -s " + device + " shell rm /mnt/sdcard/coverage.ec")

	os.chdir(apk_dir)
	ts = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
	coverage_folder = str(gen) + "." + str(pop) + "." + ts
	os.system("mkdir coverages/" + coverage_folder)
	os.system("cp bin/coverage.em coverages/" + coverage_folder)
	os.chdir("coverages/" + coverage_folder)

	# run scripts
	for index, script in enumerate(scripts):
		start_target = "adb -s " + device + " shell am instrument " + package_name + "/" + package_name + ".EmmaInstrument.EmmaInstrumentation"
		os.system(start_target)

		os.system("adb -s " + device + " push " + script + " /mnt/sdcard/.")
		script_name = script.split("/")[-1]

		# command = Command("adb -s " + device + " shell motifcore -p " + package_name + " --bugreport " + "-f /mnt/sdcard/" + script_name + " 1")
		# command.run(timeout = 180)
		cmd = "adb -s " + device + " shell motifcore -p " + package_name + " --ignore-crashes --ignore-security-exceptions --ignore-timeouts --bugreport --string-seeding /mnt/sdcard/" + package_name + "_strings.xml" + " -f /mnt/sdcard/" + script_name + " 1"
		os.system(settings.TIMEOUT_CMD + " " + str(settings.EVAL_TIMEOUT) + " " + cmd)
		# need to manually kill motifcore when timeout
		kill_motifcore_cmd = "shell ps | awk '/com\.android\.commands\.motifcore/ { system(\"adb -s " + device + " shell kill \" $2) }'"
		os.system("adb -s " + device + " " + kill_motifcore_cmd)

		if crash_handler.handle(device, apk_dir, script, gen, pop, index, unique_crashes):
			pass
		else:
			# no crash, can broadcast
			os.system("adb -s " + device + " shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE")

		# close app
		os.system("adb -s " + device + " shell pm clear " + package_name)

	print "### Getting EMMA coverage.ec and report ..."
	os.system("adb -s " + device + " shell pm clear " + package_name)
	time.sleep(0.5)
	os.system("adb -s " + device + " pull /mnt/sdcard/coverage.ec")
	os.system(
		"java -cp " + settings.ANDROID_HOME + "tools/lib/emma.jar emma report -r html -in coverage.em,coverage.ec")

	html_file = apk_dir + "/coverages/" + coverage_folder + "/coverage/index.html"
	try:
		coverage_str = extract_coverage(html_file)
	except:
		return 0, len(unique_crashes)

	if coverage_str.find("%") != -1:
		return int(coverage_str.split("%")[0]), len(unique_crashes)
	else:
		return 0, len(unique_crashes)
