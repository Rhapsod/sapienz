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
import pickle

from lxml import html
from bs4 import UnicodeDammit


def extract_coverage(path):
	with open(path, 'rb') as file:
		content = file.read()
		doc = UnicodeDammit(content, is_html=True)

	parser = html.HTMLParser(encoding=doc.original_encoding)
	root = html.document_fromstring(content, parser=parser)
	return root.xpath('/html/body/table[2]/tr[2]/td[5]/text()')[0].strip()


def cal_all_coverage(dir_path):
	in_list = ""
	for file_name in os.listdir(dir_path):
		if not (file_name.endswith(".ec") or file_name.endswith(".em")):
			continue
		in_list += file_name + ","
	in_list = in_list.strip(",")

	os.chdir(dir_path)
	cmd = "java -cp /home/kemao/Library/android-sdk-linux/tools/lib/emma.jar emma report -r html -in " + in_list
	os.system(cmd)

	return int(extract_coverage(dir_path + "/coverage/index.html").split("%")[0])


def process_collective_coverages(app_runs_dir, em_dirs, out_file, start, end):
	for i in range(start, end + 1):
		app_dirs = app_runs_dir + "/" + str(i)
		for app_dir in os.listdir(app_dirs):

			app_dir_path = app_dirs + "/" + app_dir
			if not os.path.isdir(app_dir_path + "/coverages"):
				continue

			os.chdir(app_dir_path + "/coverages")
			os.system("pwd")
			os.system("rm -rf all_coverage")
			os.system("mkdir all_coverage")

			index = 0
			for dir_name in os.listdir(app_dir_path + "/coverages"):
				ec_file_path = app_dir_path + "/coverages/" + dir_name + "/coverage.ec"
				####### NOTE Use html report as indicator, need restore verbose information first ######
				html_file_path = app_dir_path + "/coverages/" + dir_name + "/coverage/index.html"
				if os.path.exists(ec_file_path) and os.path.exists(html_file_path):
					# print "cp " + ec_file_path + " " + app_dir_path + "/coverages/all_coverage/" + str(index) + ".ec"
					os.system("cp " + ec_file_path + " " + app_dir_path + "/coverages/all_coverage/" + dir_name + ".ec")
					index += 1

			os.system("cp " + em_dirs + "/" + app_dir + "/bin/coverage.em " + app_dir_path + "/coverages/all_coverage")

		coverages = []
		for app_dir in os.listdir(app_dirs):
			app_dir_path = app_dirs + "/" + app_dir
			if not os.path.isdir(app_dir_path + "/coverages/all_coverage"):
				continue

			coverage = cal_all_coverage(app_dir_path + "/coverages/all_coverage")
			coverages.append(coverage)

		print coverages
		out_file.write(str(i) + ",Collective," + ",".join([str(x) for x in coverages]))
		out_file.write("\n")


def process_pareto_coverages(app_runs_dir, em_dirs, out_file, start, end):
	for i in range(start, end + 1):
		pareto_coverages = []
		app_dirs = app_runs_dir + "/" + str(i)
		for app_dir in os.listdir(app_dirs):
			if not os.path.exists(app_dirs + "/" + app_dir + "/intermediate/logbook.pickle"):
				pareto_coverages.append(-1)
				continue
			logbook_file = open(app_dirs + "/" + app_dir + "/intermediate/logbook.pickle")
			logbook = pickle.load(logbook_file)
			coverages = []
			for gen, gen_pop in enumerate(logbook.select("pop_fitness")):
				for indi in gen_pop:
					coverages.append(indi[0])
			pareto_coverages.append(max(coverages))

		print pareto_coverages
		out_file.write(str(i) + ",Pareto," + ",".join([str(x) for x in pareto_coverages]))
		out_file.write("\n")


if __name__ == "__main__":
	pass
