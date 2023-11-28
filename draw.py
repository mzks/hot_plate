from time import sleep
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
parser = argparse.ArgumentParser(
			prog='draw',
			description='Hotplate temperature control')

parser.add_argument('-f', '--filename', default='test')

args = parser.parse_args()
filename = args.filename+'.csv'
plt.ion()
fig = plt.figure()

while True:

	df = pd.read_csv(filename)
	plt.plot(df['time'], df['t'], label='plate')
	plt.plot(df['time'], df['t2'], label='surface')
	plt.xlabel('Time (sec.)')
	plt.ylabel('Temperature (C)')
	plt.legend()
	plt.draw()
	plt.pause(1)
	fig.clear()
