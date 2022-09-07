import base64


def print_contact():
    contact = "UVE6IDE2NjI4MDIxNTU="
    contact = str(base64.b64decode(contact), encoding="utf-8")
    print(contact)


if __name__ == '__main__':
    print_contact()


