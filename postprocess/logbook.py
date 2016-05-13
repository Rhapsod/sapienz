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


import pickle

import matplotlib.pyplot as plt


def print_pop_fitness(file_folder_path):
	logbook_file = open(file_folder_path + "logbook.pickle")

	logbook = pickle.load(logbook_file)

	for gen_pop in logbook.select("pop_fitness"):
		print gen_pop


def draw_pop_fitness(file_folder_path):
	coverages = []
	lengths = []
	colors = []  # color stands for the ith gen

	logbook_file = open(file_folder_path + "logbook.pickle")

	logbook = pickle.load(logbook_file)

	gen_size = len(logbook.select("pop_fitness"))
	for gen, gen_pop in enumerate(logbook.select("pop_fitness")):
		for indi in gen_pop:
			coverages.append(indi[0])
			lengths.append(indi[1])
			colors.append(int(gen + 1))

	# print coverages, lengths, colors

	fig, ax = plt.subplots()
	ax.set_xlabel("Length")
	ax.set_ylabel("Coverage")

	# ax.scatter(lengths, coverages, color="red", marker="^")
	im = ax.scatter(lengths, coverages, c=colors, cmap=plt.cm.jet, marker=".", s=100)

	fig.colorbar(im, ax=ax, ticks=range(1, gen_size + 1))
	im.set_clim(1, gen_size)

	fig.savefig(file_folder_path + "logbook_pop_fitness.png")
	plt.show()


if __name__ == "__main__":
	file_folder_path = "/media/kemao/Windows7_OS/bak_p500/emma_run_results/sapienz_open_p/19/com.brocktice.JustSit_17_src/intermediate/"

	print_pop_fitness(file_folder_path)
	draw_pop_fitness(file_folder_path)
