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


import random
import os
import sys
import pickle
import datetime
import subprocess
import platform
import numpy
from deap import creator, base, tools
from algorithms import eaMuPlusLambdaParallel
import settings
from coverages import emma_coverage
from coverages import ella_coverage
from coverages import act_coverage
from plot import two_d_line
from devices import emulator
from crashes import crash_handler
from analysers import static_analyser
from init import initRepeatParallel


class CanNotInitSeqException(Exception):
	pass


# get one test suite by running multiple times of MotifCore
def get_suite(device, apk_dir, package_name):
	ret = []
	unique_crashes = set()
	for i in range(0, settings.SUITE_SIZE):
		# get_sequence may return empty sequence
		seq = []
		repeated = 0
		while len(seq) <= 2:
			seq = get_sequence(device, apk_dir, package_name, i, unique_crashes)
			repeated += 1
			if repeated > 20:
				raise CanNotInitSeqException("Cannot get sequence via MotifCore.")
		ret.append(seq)

	return ret


### helper functions
# get one event sequence by running revised motifcore
# note: the luanch activity is started by emma instrument
def get_sequence(device, apk_dir, package_name, index, unique_crashes):
	std_out_file = apk_dir + "/intermediate/" + "output.stdout"
	random.seed()

	motifcore_events = random.randint(settings.SEQUENCE_LENGTH_MIN, settings.SEQUENCE_LENGTH_MAX)

	ret = []

	# clear data
	os.system("adb -s " + device + " shell pm clear " + package_name)

	# start motifcore
	print "... Start generating a sequence"
	# command = Command("adb -s " + device + " shell motifcore -p " + package_name + " -v --throttle " + str(
	# 	settings.THROTTLE) + " " + str(motifcore_events))
	# command.run(timeout=600)
	cmd = "adb -s " + device + " shell motifcore -p " + package_name + " --ignore-crashes --ignore-security-exceptions --ignore-timeouts --bugreport --string-seeding /mnt/sdcard/" + package_name + "_strings.xml -v " + str(
		motifcore_events)
	os.system(settings.TIMEOUT_CMD + " " + str(settings.EVAL_TIMEOUT) + " " + cmd)
	# need to kill motifcore when timeout
	kill_motifcore_cmd = "shell ps | awk '/com\.android\.commands\.motifcore/ { system(\"adb -s " + device + " shell kill \" $2) }'"
	os.system("adb -s " + device + " " + kill_motifcore_cmd)

	print "... Finish generating a sequence"
	# access the generated script, should ignore the first launch activity
	script_name = settings.MOTIFCORE_SCRIPT_PATH.split("/")[-1]
	ts = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.%f")[:-3]
	os.system(
		"adb -s " + device + " pull " + settings.MOTIFCORE_SCRIPT_PATH + " " + apk_dir + "/intermediate/" + script_name + ".init." + ts + "." + str(
			index))
	script = open(apk_dir + "/intermediate/" + script_name + ".init." + ts + "." + str(index))
	is_content = False
	is_skipped_first = False
	for line in script:
		line = line.strip()
		if line.find("start data >>") != -1:
			is_content = True
			continue
		if is_content and line != "":
			if is_skipped_first == False:
				is_skipped_first = True
				continue
			if is_skipped_first:
				ret.append(line)

	script.close()

	# deal with crash
	crash_handler.handle(device, apk_dir, apk_dir + "/intermediate/" + script_name + ".init." + ts + "." + str(index),
						 "init", ts, index, unique_crashes)

	return ret


# generate individual by running motifcore
def gen_individual(device, apk_dir, package_name):
	if settings.DEBUG:
		print "Generate Individual on device, ", device
	suite = get_suite(device, apk_dir, package_name)
	return (creator.Individual(suite), device)


# the suite coverage is accumulated
def eval_suite(individual, device, apk_dir, package_name, gen, pop):
	# for get_motifcore_suite_coverage
	script_path = []

	# for length objective
	suite_lengths = []
	for index, seq in enumerate(individual):
		# generate script file list
		script = open(apk_dir + "/intermediate/motifcore.evo.script." + str(gen) + "." + str(pop) + "." + str(index), "w")
		script.write(settings.MOTIFCORE_SCRIPT_HEADER)

		length = 0
		for line in seq:
			script.write(line + "\n")
			length += 1

		suite_lengths.append(length)

		script.close()
		script_path.append(os.path.abspath(
			apk_dir + "/intermediate/motifcore.evo.script." + str(gen) + "." + str(pop) + "." + str(index)))

	# give a script and package, return the coverage by running all seqs
	if apk_dir.endswith(".apk_output"):
		coverage, num_crashes = act_coverage.get_suite_coverage(script_path, device, apk_dir, package_name, gen, pop)
	else:
		coverage, num_crashes = emma_coverage.get_suite_coverage(script_path, device, apk_dir, package_name, gen, pop)
	print "### Coverage = ", coverage
	print "### Lengths = ", suite_lengths
	print "### #Crashes = ", num_crashes

	# 1st obj: coverage, 2nd: average seq length of the suite, 3nd: #crashes
	return pop, (coverage, numpy.mean(suite_lengths), num_crashes), device


def mut_suite(individual, indpb):
	# shuffle seq
	individual, = tools.mutShuffleIndexes(individual, indpb)

	# crossover inside the suite
	for i in range(1, len(individual), 2):
		if random.random() < settings.MUTPB:
			if len(individual[i - 1]) <= 2:
				print "\n\n### Indi Length =", len(individual[i - 1]), " ith = ", i - 1, individual[i - 1]
				continue  # sys.exit(1)
			if len(individual[i]) <= 2:
				print "\n\n### Indi Length =", len(individual[i]), "ith = ", i, individual[i]
				continue  # sys.exit(1)

			individual[i - 1], individual[i] = tools.cxOnePoint(individual[i - 1], individual[i])

	# shuffle events
	for i in range(len(individual)):
		if random.random() < settings.MUTPB:
			if len(individual[i]) <= 2:
				print "\n\n### Indi Length =", len(individual[i]), "ith = ", i, individual[i]
				continue  # sys.exit(1)
			individual[i], = tools.mutShuffleIndexes(individual[i], indpb)

	return individual,


def return_as_is(a):
	return a


def initRepeat(container, func, n, device, apk_dir, package_name):
	return container(func(device, apk_dir, package_name) for _ in xrange(n))


### deap framework setup
creator.create("FitnessCovLen", base.Fitness, weights=(10.0, -0.5, 1000.0))
creator.create("Individual", list, fitness=creator.FitnessCovLen)

toolbox = base.Toolbox()

toolbox.register("individual", gen_individual)

toolbox.register("population", initRepeatParallel.initPop, list, toolbox.individual)

toolbox.register("evaluate", eval_suite)
# mate crossover two suites
toolbox.register("mate", tools.cxUniform, indpb=0.5)
# mutate should change seq order in the suite as well
toolbox.register("mutate", mut_suite, indpb=0.5)
# toolbox.register("select", tools.selTournament, tournsize=5)
toolbox.register("select", tools.selNSGA2)

# log the history
history = tools.History()
# Decorate the variation operators
toolbox.decorate("mate", history.decorator)
toolbox.decorate("mutate", history.decorator)


def get_package_name(path):
	apk_path = None
	if path.endswith(".apk"):
		apk_path = path
	else:
		for file_name in os.listdir(path + "/bin"):
			if file_name == "bugroid-instrumented.apk":
				apk_path = path + "/bin/bugroid-instrumented.apk"
				break
			elif file_name.endswith("-debug.apk"):
				apk_path = path + "/bin/" + file_name

	assert apk_path is not None

	get_package_cmd = "aapt d xmltree " + apk_path + " AndroidManifest.xml | grep package= | awk 'BEGIN {FS=\"\\\"\"}{print $2}'"
	# print get_package_cmd
	package_name = subprocess.Popen(get_package_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
	return package_name, apk_path


def main(instrumented_app_dir):
	"""
	Test one apk
	:param instrumented_app_dir: The instrumentation folder of the app | apk file path for closed-source app
	"""

	host_system = platform.system()
	if host_system == "Darwin":
		print "Running on Mac OS"
		settings.TIMEOUT_CMD = "gtimeout"
	elif host_system == "Linux":
		print "Running on Linux"
	else:
		print "Runnning on unknown OS"

	package_name, apk_path = get_package_name(instrumented_app_dir)
	# for css subjects
	if instrumented_app_dir.endswith(".apk"):
		instrumented_app_dir += "_output"
		os.system("mkdir " + instrumented_app_dir)

	print "### Working on apk:", package_name

	# get emulator device
	print "Preparing devices ..."
	emulator.boot_devices()
	emulator.prepare_motifcore()
	emulator.clean_sdcard()

	# log the devices
	devices = emulator.get_devices()

	# static analysis
	if settings.ENABLE_STRING_SEEDING:
		output_dir = None
		if instrumented_app_dir.endswith(".apk_output"):
			output_dir = instrumented_app_dir
		else:
			output_dir = instrumented_app_dir + "/bin"
		static_analyser.decode_apk(apk_path, output_dir)
	# will use dummy 0 if disabled
	for device in devices:
		decoded_dir = None
		if instrumented_app_dir.endswith(".apk_output"):
			decoded_dir = instrumented_app_dir + "/" + apk_path.split("/")[-1].split(".apk")[0]
		else:
			decoded_dir = instrumented_app_dir + "/bin/" + apk_path.split("/")[-1].split(".apk")[0]
		static_analyser.upload_string_xml(device, decoded_dir, package_name)

		os.system("adb -s " + device + " shell rm /mnt/sdcard/bugreport.crash")
		os.system("adb -s " + device + " uninstall " + package_name)
		os.system("adb -s " + device + " install " + apk_path)

	# intermediate should be in app folder
	os.system("rm -rf " + instrumented_app_dir + "/intermediate")
	os.system("mkdir " + instrumented_app_dir + "/intermediate")

	os.system("rm -rf " + instrumented_app_dir + "/crashes")
	os.system("mkdir " + instrumented_app_dir + "/crashes")

	os.system("rm -rf " + instrumented_app_dir + "/coverages")
	os.system("mkdir " + instrumented_app_dir + "/coverages")

	# generate initial population
	print "### Initialising population ...."

	population = toolbox.population(n=settings.POPULATION_SIZE, apk_dir=instrumented_app_dir,
									package_name=package_name)

	print "### Individual Lengths: "
	for indi in population:
		for seq in indi:
			print len(seq),
		print ""

	history.update(population)

	# hof = tools.HallOfFame(6)
	# pareto front can be large, there is a similarity option parameter
	hof = tools.ParetoFront()

	stats = tools.Statistics(lambda ind: ind.fitness.values)
	# axis = 0, the numpy.mean will return an array of results
	stats.register("avg", numpy.mean, axis=0)
	stats.register("std", numpy.std, axis=0)
	stats.register("min", numpy.min, axis=0)
	stats.register("max", numpy.max, axis=0)
	stats.register("pop_fitness", return_as_is)

	# evolve
	print "\n\n\n### Start to Evolve"
	population, logbook = eaMuPlusLambdaParallel.evolve(population, toolbox, settings.POPULATION_SIZE,
														settings.OFFSPRING_SIZE,
														cxpb=settings.CXPB, mutpb=settings.MUTPB,
														ngen=settings.GENERATION,
														apk_dir=instrumented_app_dir,
														package_name=package_name,
														stats=stats, halloffame=hof, verbose=True)

	# persistent
	logbook_file = open(instrumented_app_dir + "/intermediate/logbook.pickle", 'wb')
	pickle.dump(logbook, logbook_file)
	logbook_file.close()

	hof_file = open(instrumented_app_dir + "/intermediate/hof.pickle", 'wb')
	pickle.dump(hof, hof_file)
	hof_file.close()

	history_file = open(instrumented_app_dir + "/intermediate/history.pickle", 'wb')
	pickle.dump(history, history_file)
	history_file.close()

	# draw graph
	two_d_line.plot(logbook, 0, instrumented_app_dir)
	two_d_line.plot(logbook, 1, instrumented_app_dir)
	two_d_line.plot(logbook, 2, instrumented_app_dir)


# draw history network
# history_network.plot(history, instrumented_app_dir)


if __name__ == "__main__":
	app_dir = sys.argv[1]
	main(app_dir)
