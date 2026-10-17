"""Generate a bcrypt password hash without exposing the password in shell history."""

from getpass import getpass
import sys

import bcrypt


def main() -> int:
    password = getpass("Password: ")
    if not password:
        print("Password cannot be empty.", file=sys.stderr)
        return 1
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        print("Passwords do not match.", file=sys.stderr)
        return 1

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    print(password_hash.decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
