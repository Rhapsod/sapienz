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


def get_diff_lines(file_path_1, file_path_2):
	with open(file_path_1, 'r') as file1:
		with open(file_path_2, 'r') as file2:
			diff_lines = set(file1).symmetric_difference(file2)

	diff_lines.discard('\n')
	return diff_lines


def get_unique_bug_reports(path):
	"""
	process one app
	:param path: */crashes/unique
	:return: number of unique bug reports, a list of bug reports path
	"""
	count = 0
	unique_bug_reports = []

	unique_bug_reports_path = path + "/unique"
	try:
		os.system("rm -rf " + unique_bug_reports_path)
		os.system("mkdir " + unique_bug_reports_path)
	except:
		pass

	for file_name in os.listdir(path):
		if file_name.endswith(".bugreport"):
			file_path = path + "/" + file_name
			is_unique = True
			for existing_file_path in unique_bug_reports:
				if len(get_diff_lines(file_path, existing_file_path)) <= 2:
					is_unique = False
					# rm from the folder
					prefix = file_name.split(".bugreport")[0]
					os.system("rm " + path + "/" + prefix + "*")
					break
			if is_unique:
				unique_bug_reports.append(file_path)
				count += 1
				# cp report and test suite
				prefix = file_name.split(".bugreport")[0]
				os.system("cp " + path + "/" + prefix + "*" + " " + unique_bug_reports_path)

	print count
	print unique_bug_reports

	return count, unique_bug_reports


def get_all_unique_bug_reports(path):
	"""
	save a set of unique bug reports under crashes/unique/
	each report comes with its test suite
	:param path: ella output path
	:returns total number of unique bug reports, a list of bug reports path
	"""

	# a set of file paths of the *.bugreport
	unique_bug_reports = []
	count = 0

	for folder_name in os.listdir(path):
		apk_folder_path = path + "/" + folder_name
		if not os.path.isdir(apk_folder_path):
			continue
		crashes_folder_path = apk_folder_path + "/crashes"
		if not os.path.isdir(crashes_folder_path):
			continue

		tmp_count, tmp_reports = get_unique_bug_reports(crashes_folder_path)
		count += tmp_count
		unique_bug_reports.extend(tmp_reports)

	return count, unique_bug_reports


if __name__ == "__main__":
	ella_output_path = "/home/kemao/test/apk/ella_output"

	count, report_paths = get_all_unique_bug_reports(ella_output_path)
	print "Total:", count
	print report_paths
