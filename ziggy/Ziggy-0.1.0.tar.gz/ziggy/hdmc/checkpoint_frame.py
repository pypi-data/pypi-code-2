#! /usr/bin/env python

from glob import glob
import sys, os, subprocess, shlex, random, time, re

def main():
	time.sleep(random.random())
	all_checkpoints = ['20417.txt', '132.txt', '19699.txt', '4300.txt', '972.txt', '7ldvc10.txt', 'advsh12.txt']
	this_checkpoint = random.choice(all_checkpoints)
	current_checkpoints = glob('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/*')
	for i in range(len(current_checkpoints)):
		current_checkpoints[i] = re.sub('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/', '', current_checkpoints[i])
	while this_checkpoint in current_checkpoints:
		this_checkpoint = random.choice(all_checkpoints)
		current_checkpoints = glob('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/*')
		for i in range(len(current_checkpoints)):
			current_checkpoints[i] = re.sub('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/', '', current_checkpoints[i])
		if len(current_checkpoints) == len(all_checkpoints):
			exit()
	
	subprocess.call(['touch','/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints'+'/'+this_checkpoint])
	subprocess.call(['chmod','777','/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints'+'/'+this_checkpoint])
	os.system('chmod a+rwx line_counter.py')
	cmd = ['./line_counter.py']+['./'+this_checkpoint]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, error = p.communicate()
	sts = p.wait()
	print output


if __name__ == "__main__":
	main()
	

