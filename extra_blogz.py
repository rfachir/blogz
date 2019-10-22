import hashlib    #jesicas hashutils
import random
import string


def salt_it():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def make_pw_hash(password, salt=None):
    if not salt:
        salt = salt_it()

    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return '{0},{1}'.format(hash,salt)

def check_pw_hash(password, hash):
    salt = hash.split(',')[1]
    if make_pw_hash(password, salt) == hash:
        return True
    else:
        return False