from config import OUTPUT_PATH
import os


os.system('rm -rvf %s' % OUTPUT_PATH)
os.system('mkdir -pv %s' % OUTPUT_PATH)
os.system('mkdir -pv %s' % os.path.join(OUTPUT_PATH, 'logs'))
execfile('analysis.py')
execfile('comparison.py')
