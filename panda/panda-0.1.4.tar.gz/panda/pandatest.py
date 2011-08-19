import panda
panda = panda.Panda(
    api_host='staging.pandastream.com',
    cloud_id='537cb0311b9aafc530f9ff1c0377d787',
    access_key='a7704c6c854d69a031d8',
    secret_key='efe1c61c3edfc7772556'
)
print panda.get('/profiles.json')
print panda.put('/notifications.json', {"events": {"encoding_completed": "true" }})

