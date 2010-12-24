# Pre-built replacers.

varchar = lambda anon, obj, field, val: anon.faker.varchar(field=field)
bool = lambda anon, obj, field, val: anon.faker.bool(field=field)
integer = lambda anon, obj, field, val: anon.faker.integer(field=field)
positive_integer = lambda anon, obj, field, val: anon.faker.positive_integer(field=field)
small_integer = lambda anon, obj, field, val: anon.faker.small_integer(field=field)
positive_small_integer = lambda anon, obj, field, val: anon.faker.positive_small_integer(field=field)
datetime = lambda anon, obj, field, val: anon.faker.datetime(field=field)
date = lambda anon, obj, field, val: anon.faker.date(field=field)
uk_postcode = lambda anon, obj, field, val: anon.faker.uk_postcode(field=field)
uk_country = lambda anon, obj, field, val: anon.faker.uk_country(field=field)
uk_county = lambda anon, obj, field, val: anon.faker.uk_county(field=field)
username = lambda anon, obj, field, val: anon.faker.username(field=field)
first_name = lambda anon, obj, field, val: anon.faker.first_name(field=field)
last_name = lambda anon, obj, field, val: anon.faker.last_name(field=field)
name = lambda anon, obj, field, val: anon.faker.name(field=field)
email = lambda anon, obj, field, val: anon.faker.email(field=field)
full_address = lambda anon, obj, field, val: anon.faker.full_address(field=field)
phonenumber = lambda anon, obj, field, val: anon.faker.phonenumber(field=field)
street_address = lambda anon, obj, field, val: anon.faker.street_address(field=field)
city = lambda anon, obj, field, val: anon.faker.city(field=field)
state = lambda anon, obj, field, val: anon.faker.state(field=field)
zip_code = lambda anon, obj, field, val: anon.faker.zip_code(field=field)
company = lambda anon, obj, field, val: anon.faker.company(field=field)
lorem = lambda anon, obj, field, val: anon.faker.lorem(field=field)

# These use the value of the field to return a date/datetime that is close
# (within two years) of the original value.
similar_datetime = lambda anon, obj, field, val: anon.faker.datetime(field=field, val=val)
similar_date = lambda anon, obj, field, val: anon.faker.date(field=field, val=val)

# similar_lorem produces lorem ipsum text with the same length and same pattern
# of linebreaks as the original. If the original often takes a standard form
# (e.g. a single word 'yes' or 'no'), this could easily fail to hide the
# original data.
similar_lorem = lambda anon, obj, field, val: anon.faker.lorem(field=field, val=val)

