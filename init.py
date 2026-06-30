import os.path


def create_init_files() -> None:
    """
    Checks to see if a client_secrets.json file exists, and if if doesn't, it raises a FileNotFoudnError with a message to teh user to create one.
    """

    try:
        os.path.isfile("client_secrets.json")
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "client_secrets.json file not found. Please create one by going through the README.md, creating a google cloud project, creating a client_secrets.json, and placing it in the root directory."
        ) from e
