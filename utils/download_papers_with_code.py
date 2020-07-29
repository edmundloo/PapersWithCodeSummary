import gzip
import json
import requests


def get_gzipped_json_from_url(url):
    """
    Download and uncompress gzipped data from a given URL, returning a dict
    representing JSON data.
    """
    request_compressed = requests.get(url)
    request_content = gzip.decompress(request_compressed.content)
    json_data = json.loads(request_content)
    return json_data


def build_paper_data_with_proceeding_dict(paper_data, paper_to_proceeding):
    """
    Given a mapping of paper to GitHub URLs and paper to proceeding, build
    a dict that contains a mapping of paper abstract URL to a dict that
    contains paper data, proceeding, and GitHub URL.
    """
    result_dict = dict()
    for paper in paper_data:
        result_dict[paper["paper_url_abs"]] = paper
        result_dict[paper["paper_url_abs"]]["proceeding"] = ""
    for paper in paper_to_proceeding:
        if paper["url_abs"] in result_dict:
            result_dict[paper["url_abs"]]["proceeding"] = paper["proceeding"]
    return result_dict
