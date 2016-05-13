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
import sys
import shutil
import xml.etree.cElementTree as ET

from lxml import etree

import settings


def compile_apk(path, package_name, devices):
	os.chdir(path)
	os.system("android update project --target " + settings.ANDROID_TARGET + " --path ./ --name bugroid")
	os.system("ant instrument")
	os.system("cd bin")
	print "... uninstall existed version"

	for device in devices:
		os.system("adb -s " + device + " uninstall " + package_name)
		os.system("adb -s " + device + " install " + path + "/bin/bugroid-instrumented.apk")

	# start_target = "adb -s " + device + " shell am instrument " + package_name + "/" + package_name + ".EmmaInstrument.EmmaInstrumentation"
	# os.system( start_target )


def get_main_activity(root_path):
	manifest = root_path + "AndroidManifest.xml"

	tree = etree.parse(manifest)
	root = tree.getroot()
	namespace = dict(android='http://schemas.android.com/apk/res/android')
	return root.xpath(".//intent-filter/action[@android:name='android.intent.action.MAIN']/../../@android:name",
					  namespaces=namespace)[0]


def get_package_name(root_path):
	manifest = root_path + "AndroidManifest.xml"

	tree = ET.ElementTree(file=manifest)

	return tree.getroot().attrib["package"]


def alter_AndroidManifest(path, package_name):
	is_mod = False

	content = ""
	in_stream = open(path)
	for index, line in enumerate(in_stream):
		if line.find("</application>") != -1:

			content += \
				'''

				 <!-- emma updated -->
				<activity android:label="EmmaInstrumentationActivity" android:name="''' + package_name + '''.EmmaInstrument.InstrumentedActivity"/>
			<receiver android:name="''' + package_name + '''.EmmaInstrument.SMSInstrumentedReceiver">
				<intent-filter>
				<action android:name="edu.gatech.m3.emma.COLLECT_COVERAGE" />
				</intent-filter>
			</receiver>
			 <!-- emma updated -->
			 
			''' + line + '''
			 <!-- emma updated -->
			 <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>  
			 <instrumentation android:handleProfiling="true" android:label="EmmaInstrumentation" android:name="''' + package_name + '''.EmmaInstrument.EmmaInstrumentation" android:targetPackage="''' + package_name + '''"/>
			 <!-- emma updated -->

			'''
			is_mod = True
		else:
			content += line

	in_stream.close()
	os.remove(path)
	new_file = open(path, "w")
	new_file.write(content)
	new_file.close()

	if is_mod == False:
		print "[Error] Failed when update AndroidManifest.xml"


def alter_InstrumentedActivity(path, main_activity):
	content = ""

	in_stream = open(path)

	for index, line in enumerate(in_stream):
		if line.find("public class InstrumentedActivity extends com.totsp.bookworm.Main {") != -1:
			content += "public class InstrumentedActivity extends " + main_activity + " {\n"
		else:
			content += line

	in_stream.close()
	os.remove(path)
	new_file = open(path, "w")
	new_file.write(content)
	new_file.close()


def alter_emma_file(path, package):
	content = ""

	in_stream = open(path)

	for index, line in enumerate(in_stream):
		if index == 0:
			content += "package " + package + ".EmmaInstrument;\n"
		else:
			content += line

	in_stream.close()
	os.remove(path)
	new_file = open(path, "w")
	new_file.write(content)
	new_file.close()


def main(devices):
	project_folder = settings.PROJECT_FOLDER

	if os.path.exists(settings.EMMA_ED + project_folder):
		shutil.rmtree(settings.EMMA_ED + project_folder)
	shutil.copytree(settings.ORIGINAL_PATH + project_folder, settings.EMMA_ED + project_folder)

	# get package name
	print "... get package name"
	package_name = get_package_name(settings.EMMA_ED + project_folder + "/")

	# copy emma source # TODO: may need to modify src path
	print "... copy emma source"
	source_root = settings.EMMA_ED + project_folder + "/src/" + "/".join(package_name.split(".")) + "/"
	os.chdir(source_root)
	shutil.copytree(settings.ORIGINAL_PATH + "EmmaInstrument", source_root + "EmmaInstrument")

	# modify emma source
	print "... modify emma source"
	for target in os.listdir(source_root + "EmmaInstrument"):
		if target.endswith(".java"):
			alter_emma_file(source_root + "EmmaInstrument/" + target, package_name)

	# get & alter based on main activity based on "android.intent.action.MAIN"
	print "... get main activity"
	main_activity = get_main_activity(settings.EMMA_ED + project_folder + "/")
	if main_activity.startswith("."):
		main_activity = package_name + main_activity
	print "... =", main_activity

	# modify InstrumentedActivity.java
	print "... update main activity in InstrumentedActivity.java"
	alter_InstrumentedActivity(source_root + "EmmaInstrument/InstrumentedActivity.java", main_activity)

	# update AndroidManifest.xml
	print "... update AndroidManifest.xml"
	alter_AndroidManifest(settings.EMMA_ED + project_folder + "/AndroidManifest.xml", package_name)

	# compile
	print "... compile apk and start"
	compile_apk(settings.EMMA_ED + project_folder, package_name, devices)

	print "Done."
