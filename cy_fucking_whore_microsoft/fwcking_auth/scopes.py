import typing


def get_one_drive()->typing.List[str]:
    return [
        'User.Read',
        'User.Read.All',
        'User.ReadWrite',
        'User.ReadWrite.All',
        'Files.Read',
        'Files.Read.All',
        'Files.ReadWrite',
        'Files.ReadWrite.All'
    ]
def get_account()->typing.List[str]:
    return [
        "User.Invite.All"
    ]