from time import sleep
import argparse
import RPi.GPIO as G
import sys
from daqhats import hat_list, HatIDs, mcc134
from simple_pid import PID

parser = argparse.ArgumentParser(
			prog='ctl',
			description='Hotplate temperature control')

parser.add_argument('-t', '--target', default=40., type=float)
parser.add_argument('-s', '--sec', default=10., type=float)
parser.add_argument('-f', '--filename', default='test')

args = parser.parse_args()

RELAY_GPIO = 23

G.setmode(G.BCM)
G.setwarnings(False)
G.setup(RELAY_GPIO, G.OUT)

G.output(RELAY_GPIO, G.LOW)

address = 0
channel = 0
hat = mcc134(address)
hat.tc_type_write(channel, 2) # 2 -> TC-T
hat.tc_type_write(1, 2) # 2 -> TC-T

pid = PID(100,100,100, setpoint=args.target)
#pid = PID(1, 0.1, 0.05, setpoint=args.target)
pid.output_limits = (0,1)

f = open(args.filename + '.csv', mode='w')
f.write('time,t,t2\n')

status = 'warming'
sleep_sec = 0.1
n_loops = 0
total_time = 0
target_time = 0

def switching(duty, cycle_sec):
	if duty > 0.98:
		G.output(RELAY_GPIO, G.HIGH)
		sleep(cycle_sec)
		return
	if duty < 0.02:
		G.output(RELAY_GPIO, G.LOW)
		sleep(cycle_sec)
		return
	G.output(RELAY_GPIO, G.HIGH)
	sleep(cycle_sec*duty)
	G.output(RELAY_GPIO, G.LOW)
	sleep(cycle_sec*(1.-duty))
	
	return

G.output(RELAY_GPIO, G.HIGH)
while True:
	t = hat.t_in_read(channel)
	t2 = hat.t_in_read(1)
	control = pid(t)

	s = '{} : {:.1f} C, {:.1f} C, {:.1f} sec., power {:.2f}'.format(status, t, t2, target_time, control)
	sys.stdout.write("\033[2K\033[G%s" % s)
	sys.stdout.flush()
	f.write('{},{},{}\n'.format(total_time, t, t2))
	f.flush()
	
	if status is 'off':
		sleep(sleep_sec)
	else:
		switching(control, sleep_sec)

	n_loops += 1
	total_time += sleep_sec
	if t >= args.target:
		status = 'on_target'
	if status == 'on_target':
		target_time += sleep_sec
	if target_time >= args.sec:
		status = 'off'
		G.output(RELAY_GPIO, G.LOW)
		
