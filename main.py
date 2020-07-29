import sys

from cli_service import (
    update_db,
    show_proceeding_tools,
    show_proceeding_tools_percentage,
    show_tools,
)


def main():
    commands = [
        "update_db",
        "show_tools",
        "show_proceeding_tools",
        "show_proceeding_tools_percentage",
    ]

    default_message = """
CLI Usage:
    python3 main.py update_db
        - Pulls new information from Papers With Code and adds
          new papers to DB.
    python3 main.py show_tools
        - Shows the unique tools for each paper in the format:
          "abstract_url: tool1, tool2, tool3"
    python3 main.py show_proceeding_tools
        - Shows the unique tools for each proceeding in the format:
          "proceeding: tool1, tool2, tool3"
    python3 main.py show_proceeding_tools_percentage
        - Shows the popularity of individual tools for
          each proceeding in the format:
            {
                proceeding: {
                    tool1: amount - percentage,
                    tool2: amount - percentage,
                    tool3: amount - percentage,
                }
            }
    """
    if len(sys.argv) != 2:
        print("Wrong number of arguments.")
        print(default_message)
    elif sys.argv[-1].lower() not in commands:
        print("Wrong command.")
        print(default_message)
    elif sys.argv[-1].lower() == "update_db":
        update_db()
    elif sys.argv[-1].lower() == "show_tools":
        show_tools()
    elif sys.argv[-1].lower() == "show_proceeding_tools":
        show_proceeding_tools()
    elif sys.argv[-1].lower() == "show_proceeding_tools_percentage":
        show_proceeding_tools_percentage()
    else:
        print("Invalid input.")
        print(default_message)


if __name__ == "__main__":
    main()
