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

import settings


def extract_axis(array, axis):
	ret = []
	for elem in array:
		ret.append(elem[axis])
	return ret


def plot(logbook, axis, apk_dir):
	gen = logbook.select("gen")
	fit_avg = extract_axis(logbook.select("avg"), axis)
	fit_min = extract_axis(logbook.select("min"), axis)
	fit_max = extract_axis(logbook.select("max"), axis)

	fig, ax1 = plt.subplots()
	line1 = ax1.plot(gen, fit_avg, "b-", label="Avg Fitness")
	line2 = ax1.plot(gen, fit_min, "r-", label="Min Fitness")
	line3 = ax1.plot(gen, fit_max, "g-", label="Max Fitness")
	ax1.set_xlabel("Generation")
	ax1.set_ylabel("Obj.-" + str(axis), color="b")
	for tl in ax1.get_yticklabels():
		tl.set_color("b")

	lns = line1 + line2 + line3
	labs = [l.get_label() for l in lns]
	leg = ax1.legend(lns, labs, loc="upper right", frameon=False)
	leg.get_frame().set_alpha(0.5)
	# plt.show()
	fig = plt.gcf()
	fig.set_size_inches(18.5, 10.5)
	fig.savefig(apk_dir + '/intermediate/obj_' + str(axis) + '.pdf', dpi=300)


if __name__ == "__main__":
	logbook = pickle.load(open(settings.WORKING_DIR + "intermediate/logbook.pickle"))
	plot(logbook, 0)
