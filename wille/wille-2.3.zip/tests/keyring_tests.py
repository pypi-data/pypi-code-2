import sys; sys.path.append('..')

# Keyring management tests
import wille.auth

# 1. Creating a keyring with one of each basic type
keyring = wille.auth.Keyring()
keyring.add_token_apikey('1234567890abcdefg', domain='api.example.com')
keyring.add_token_username('myusername', '@1234abcdABCDEF^[]', domain='www.example.com')
assert len(keyring.keys()) == 2, "keyring add failed"

# 2. Serialize keyring and reload it
keyring.save('test.keyring')
keyring2 = wille.auth.Keyring(filename='test.keyring')
keyring2.load('test.keyring')
assert len(keyring.keys()) == len(keyring2.keys()), "keyring serialization failed"
www_example_com_keys = keyring.keys(domain='www.example.com')
assert (len(www_example_com_keys)==1)
assert (www_example_com_keys[0].username=='myusername')
assert (www_example_com_keys[0].password=='@1234abcdABCDEF^[]')

# 3. Add keys with different scopes:
keyring2 = wille.auth.Keyring()
keyring2.add_token_username('examplecomall','12121212', domain='example.com')
keyring2.add_token_username('apiexamplecom','12121212', domain='api.example.com')

# 3. Search for keys by domain
# 3.1. Match any keys within a domain (*example.com)
assert( len(keyring2.keys(domain='example.com')) == 1 )
# 3.2. Match any keys within a subdomain (*api.example.com*)
assert( len(keyring2.keys(domain='api.example.com')) == 2 )
# 3.3. Match any keys within a subdomain+directory (*api.example.com*)
assert( len(keyring2.keys(domain='api.example.com/v2')) == 2 )

# Keyring tests: test core token types 
keyring3 = wille.auth.Keyring()
keyring3.add_token_username('username', 'password', 'example.com')
keyring3.add_token_apikey('API_KEY', 'Secret', 'api.example.com')
assert( keyring3.keys(type='UsernameToken', domain='example.com')[0].username == 'username' )
assert( keyring3.keys(type='UsernameToken', domain='example.com')[0].password == 'password' )
assert( keyring3.keys(type='APIKeyToken', domain='api.example.com')[0].api_key == 'API_KEY' )
assert( keyring3.keys(type='APIKeyToken', domain='api.example.com')[0].secret == 'Secret' )
