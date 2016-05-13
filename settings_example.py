DEBUG = False
ENABLE_STRING_SEEDING = True
HEADLESS = False



# === Emualtor ===
DEVICE_NUM = 2
AVD_BOOT_DELAY = 60
AVD_SERIES = "emu"
EVAL_TIMEOUT = 120
TIMEOUT_CMD = "timeout" # "gtimeout" for MacOS


# === Env. Paths ===
#     path should end with a '/'
ANDROID_HOME = '/home/sapienz/Library/android-sdk-linux/'
WORKING_DIR = '/home/sapienz/Desktop/sapienz_open_release/'



# === GA parameters ===
SEQUENCE_LENGTH_MIN = 20
SEQUENCE_LENGTH_MAX = 500 # 1000
SUITE_SIZE = 5
POPULATION_SIZE = 50 # MU
OFFSPRING_SIZE = 50 # LAMBDA
GENERATION = 100
# Crossover probability
CXPB = 0.7
# Mutation probability
MUTPB = 0.3



# === Only for main_multi ===
APK_OFFSET = 0 # start from ith apk
APK_DIR = ""
REPEATED_RESULTS_DIR = ""
REPEATED_RUNS = 20


# === MOTIFCORE script ===
# for initial population
MOTIFCORE_SCRIPT_PATH = '/mnt/sdcard/motifcore.script'
# header for evolved scripts
MOTIFCORE_SCRIPT_HEADER = 'type= raw events\ncount= -1\nspeed= 1.0\nstart data >>\n'