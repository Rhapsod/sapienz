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

import networkx

import settings


def plot(history, apk_dir):
	graph = networkx.DiGraph(history.genealogy_tree)
	# graph = graph.reverse()     # Make the grah top-down
	# colors = [toolbox.evaluate(history.genealogy_history[i])[0] for i in graph]
	# networkx.draw(graph, node_color=colors)
	# networkx.draw(graph)
	# plt.show()
	networkx.write_dot(graph, apk_dir + '/intermediate/tmp.dot')
	# same layout using matplotlib with no labels
	plt.title("History Network")
	pos = networkx.graphviz_layout(graph, prog='dot', scale=10)
	networkx.draw(graph, pos, with_labels=False, arrows=False, node_size=30)

	fig = plt.gcf()
	fig.set_size_inches(18.5, 10.5)
	fig.savefig(apk_dir + '/intermediate/history_network.pdf', dpi=300)


if __name__ == "__main__":
	print "Test"
	history_pickle = open(settings.WORKING_DIR + "intermediate/history.pickle")
	history = pickle.load(history_pickle)
	plot(history)
