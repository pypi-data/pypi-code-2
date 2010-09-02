req1 = {
    "method": "POST",
    "uri": uri("/two_chunks_mult_zero_end"),
    "version": (1, 1),
    "headers": [
        ("TRANSFER-ENCODING", "chunked")
    ],
    "body": "hello world"
}

req2 = {
    "method": "GET",
    "uri": uri("/second"),
    "version": (1, 1),
    "headers": [],
    "body": ""
}

request = [req1, req2]