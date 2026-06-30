from googleapiclient import discovery

from auth import login_google
from init import create_init_files


def main() -> None:
    """
    Main function to run the election script.
    """
    create_init_files()
    form_service: discovery.Resource = login_google()
    print(type(form_service))


if __name__ == "__main__":
    main()
