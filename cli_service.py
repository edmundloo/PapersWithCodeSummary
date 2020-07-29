import json
import time
from collections import defaultdict

import pickledb
from github import Github
from models.paper_with_code import PaperWithCode
from plugins.paper_with_code_plugins import ALL_PLUGINS
from utils.download_papers_with_code import (
    build_paper_data_with_proceeding_dict,
    get_gzipped_json_from_url,
)

# Hardcoded links to download Papers With Code
LINKS_BETWEEN_PAPERS_AND_CODE_DATA_URL = (
    "https://paperswithcode.com/media/about/links-between-papers-and-code.json.gz"
)
PAPERS_WITH_ABSTRACT_DATA_URL = (
    "https://paperswithcode.com/media/about/papers-with-abstracts.json.gz"
)

# Put your GH token here
GH_ACCESS_TOKEN = ""

# Initialize the DB, we need this for every command
PAPERS_DB = pickledb.load("papers.db", False)


def update_db():
    """
    Used by the CLI in order to populate/update the DB with paper information.
    """

    def store_paper_info(papers_db, paper, gh_api):
        """
        Run logic to get updated information on paper and send to DB.
        """

        # Only call API on paper if we don't already have the information
        if not papers_db.exists(paper["paper_url_abs"]):
            try:
                print(f'Processing paper: "{paper}"')
                pwc = PaperWithCode(paper, gh_api)

                # Apply all heuristics plugins to paper
                pwc.apply_plugins(ALL_PLUGINS)
            except Exception as e:
                print(f'Error on paper: "{paper}" and error: "{e}"')
                if "Not Found" in str(e):
                    # If not found, continue
                    return True
                return False
            else:
                # We need to serialize the PaperWithCode before storing it
                serialized_pwc = pwc.serialize()
                print(
                    "Do NOT shut down script, "
                    f'adding paper to DB: "{serialized_pwc}"'
                )
                papers_db.set(paper["paper_url_abs"], serialized_pwc)
                papers_db.dump()
                print(f'Successfully added paper to DB: "{serialized_pwc}"')
                return True

    # Get the data which includes the papers and the links to the GitHub Repos
    paper_data = get_gzipped_json_from_url(LINKS_BETWEEN_PAPERS_AND_CODE_DATA_URL,)
    paper_to_proceeding = get_gzipped_json_from_url(PAPERS_WITH_ABSTRACT_DATA_URL,)
    paper_data_dict = build_paper_data_with_proceeding_dict(
        paper_data, paper_to_proceeding,
    )

    gh_api = Github(GH_ACCESS_TOKEN)

    keep_running = True
    for paper in paper_data_dict:
        keep_running = store_paper_info(PAPERS_DB, paper_data_dict[paper], gh_api,)

        # Keep retrying with a delay if we hit rate limit
        while keep_running == False:
            print(
                "Sleeping, if you want to pause and resume updating the DB "
                "later, shut down the script within 60 seconds."
            )
            time.sleep(60)
            print("Retrying, do not shut down script.")
            keep_running = store_paper_info(PAPERS_DB, paper_data_dict[paper], gh_api,)


def show_tools():
    """
    Used by the CLI to show tools for each paper.
    """
    all_keys = PAPERS_DB.getall()
    for key in all_keys:
        p = PAPERS_DB.get(key)
        tools_string = ", ".join(p["plugin_output"])
        print(f"{key}: {tools_string}")


def show_proceeding_tools():
    """
    Used by the CLI to show tools for each proceeding.
    """
    all_keys = PAPERS_DB.getall()
    proceeding_agg = defaultdict(set)
    for key in all_keys:
        paper = PAPERS_DB.get(key)

        # Maintain a set of unique tools used for a certain proceeding
        plugin_set = set(paper["plugin_output"])
        proceeding_agg[paper["proceeding"].upper()] |= plugin_set
    for proceeding in proceeding_agg:
        tools_string = ", ".join(proceeding_agg[proceeding])
        print(f"{proceeding}: {tools_string}")


def show_proceeding_tools_percentage():
    """
    Used by the CLI to show tools along with count and percentage of total
    tools for each proceeding.
    """
    all_keys = PAPERS_DB.getall()
    proceeding_agg = defaultdict(lambda: defaultdict(int))
    for key in all_keys:
        paper = PAPERS_DB.get(key)

        # Count the amount of times a tool is used per proceeding
        for plugin_output in paper["plugin_output"]:
            proceeding_agg[paper["proceeding"].upper()][plugin_output] += 1
    for proceeding in proceeding_agg:
        proceeding_stats = dict()
        proceeding_stats[proceeding] = dict()

        total_papers = sum(proceeding_agg[proceeding].values())

        # Calculate statistics per tool per proceeding
        for tool in proceeding_agg[proceeding]:
            tool_count = proceeding_agg[proceeding][tool]
            tool_percentage = 100 * (tool_count / total_papers)
            proceeding_stats[proceeding][tool] = f"{tool_count} - {tool_percentage}%"

        # Print nicely formatted JSON statistics for each proceeding
        pretty_tools_string = json.dumps(proceeding_stats, sort_keys=True, indent=4,)
        print(pretty_tools_string)
