def get_boolean(prompt=''):
	resp = input(prompt)
	return resp == 'yes'

def get_int(prompt=''):
        resp = input(prompt)
        return int(resp)

def get_string(prompt=''):
        return input(prompt)
