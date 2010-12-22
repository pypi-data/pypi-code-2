#! /usr/bin/env python

from glob import glob
import sys, os, subprocess, shlex, random, time, re

def main():
	wait_counter = 1
	time.sleep(random.random())
	all_checkpoints = ['0', '1', '2', '3', '4', '5', '6']
	this_checkpoint = random.choice(all_checkpoints)
	this_checkpoint_start = this_checkpoint+'_start'
	this_checkpoint_end = this_checkpoint+'_end'
	current_checkpoints = glob('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/*')
	final_checkpoints = glob('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/*_end')
	while len(final_checkpoints) < len(all_checkpoints):
		for i in range(len(current_checkpoints)):
			current_checkpoints[i] = re.sub('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/', '', current_checkpoints[i])
		while this_checkpoint_end in current_checkpoints:
			this_checkpoint = random.choice(all_checkpoints)
			this_checkpoint_start = this_checkpoint+'_start'
			this_checkpoint_end = this_checkpoint+'_end'
			current_checkpoints = glob('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/*')
			final_checkpoints = glob('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/*_end')
			for i in range(len(current_checkpoints)):
				current_checkpoints[i] = re.sub('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/', '', current_checkpoints[i])
			if len(final_checkpoints) == len(all_checkpoints):
				exit()
		
		subprocess.call(['touch','/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints'+'/'+this_checkpoint+'_start'])
		subprocess.call(['chmod','777','/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints'+'/'+this_checkpoint+'_start'])
		os.system('chmod a+rwx fetch_books.py')
		argf = open('./'+this_checkpoint).readlines()
		for i in range(len(argf)):
			argf[i] = argf[i].strip()
		cmd = ['./fetch_books.py']+argf
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, error = p.communicate()
		sts = p.wait()
		output = output.strip()
		if len(output) > 0:
			line_count = 0
			newline = '\n'
			for line in output.split(newline):
				print this_checkpoint+'==HDMC_CHECKPOINT==LINE=='+ str(line_count) + '=='+line.strip()
				line_count += 1
		if len(error.strip()) > 0:
			print >> sys.stderr, error.strip()
			os.system('rm /usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints'+'/'+this_checkpoint)
			exit(1)
		else:
			subprocess.call(['touch','/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints'+'/'+this_checkpoint+'_end'])
			subprocess.call(['chmod','777','/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints'+'/'+this_checkpoint+'_end'])
		os.system('rm /usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/'+this_checkpoint+'_start')
		subprocess.call(['touch','/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints'+'/'+this_checkpoint+'_end'])
		this_checkpoint = random.choice(all_checkpoints)
		current_checkpoints = glob('/usr/local/hadoop/user-tmp/dwmclary/hdmc_checkpoints/*')


if __name__ == "__main__":
	main()
	

