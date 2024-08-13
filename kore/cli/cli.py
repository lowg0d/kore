import argparse
import os


def create_project(name):
    print(f"Created new project: {name}")


def main():
    parser = argparse.ArgumentParser(description="PySide6 Helper CLI")
    parser.add_argument("command", choices=["create"], help="Command to execute")
    parser.add_argument("name", help="Name of the project")

    args = parser.parse_args()

    if args.command == "create":
        create_project(args.name)


if __name__ == "__main__":
    main()
