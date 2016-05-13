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

from lxml import html
from bs4 import UnicodeDammit

import settings


def extract_coverage(path):
	with open(path, 'rb') as file:
		content = file.read()
		doc = UnicodeDammit(content, is_html=True)

	parser = html.HTMLParser(encoding=doc.original_encoding)
	root = html.document_fromstring(content, parser=parser)
	return root.xpath('/html/body/table[2]/tr[2]/td[5]/text()')[0].strip()


if __name__ == "__main__":

	PROJECT_FOLDER = "com.brocktice.JustSit_17_src"

	coverages = []

	for coverage_folder in os.listdir(settings.EMMA_ED + PROJECT_FOLDER + "/coverages/"):
		try:
			html_file = settings.EMMA_ED + settings.PROJECT_FOLDER + "/coverages/" + coverage_folder + "/coverage/index.html"
			coverage_str = extract_coverage(html_file)
			coverages.append(int(coverage_str.split("%")[0]))
		except:
			pass

	print max(coverages)
	print "len", len(coverages)

