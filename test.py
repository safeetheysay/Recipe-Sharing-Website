from werkzeug.security import generate_password_hash, check_password_hash

generate_password_hash('123') 
print(generate_password_hash('123'))

print(check_password_hash(generate_password_hash('123'), '123'))
