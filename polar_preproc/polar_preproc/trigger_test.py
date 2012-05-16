import trigger
##import region_collector
##from pyresample import utils

input_dirs = ['tests/data',]

##regions = [utils.load_area('tests/region_collector/areas.def', 'marcoast'), ]

collector_functions =  [] #[ region_collector.Collector(region).collect for region in regions ]

# timeout not handled 
# should be able to handle both inotify, database events or posttroll messages
# metadata should be decoded.


def terminator(metadata):
    print metadata

decoder = None

granule_trigger = trigger.FileTrigger(collector_functions, terminator, decoder, input_dirs)

try:
    granule_trigger.loop()
except KeyboardInterrupt:
    print "Thank you for using pytroll"
    pass


