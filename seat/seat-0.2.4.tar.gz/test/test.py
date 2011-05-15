import seat
database = seat.Seat('http://7FFFD85B8C28637EEE7EB9DD538B7A4E1245A481:1D8496B264C6EC6A5006EC3AB7C6727846D51927@localhost:5984/stackd_grid')
print database.view('site',
    'by_user_username',
    startkey='{"user_username":"%s", "position":%s, "position_updated_at_i":%s}'
    % ('fred', 0, 0),
    endkey='{"user_username":"%s", "position":%s, "position_updated_at_i":%s}'
    % ('fred', 9999999999, 9999999999)
)
