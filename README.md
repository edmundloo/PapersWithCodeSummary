# Papers With Code Summary

## Background

[Papers With Code](https://paperswithcode.com/) is a web archive of machine learning papers with a GitHub repository attached to give readers some concrete examples of the topics described in the paper. We want to be able to look at these papers by the kind of machine learning tool that is used in the ML code, but this information is not directly provided by the archive. We also want to be able to look at the popularity of ML tools aggregated by the proceeding in which the paper is associated with. The proceeding is given by Papers With Code, but we need to first figure out what tools are used in the code in order to create these aggregates.

## Solution

In this particular example, we are looking to identify if any of the given five technologies are used by the code: NumPy, SciPy/scikit-learn, TensorFlow, PyTorch, or MATLAB. I built a light framework that allows you to initialize `PaperWithCode` objects given information on a paper and then you can write `BasePaperWithCodePlugin` classes in order to run your heuristics of choice on the GitHub repository.

The heuristics that I used are fairly primitive and are as follows:

- NumPy: Use the GitHub search API to look through the code base for any case-insensitive appearance of the string "numpy"
- SciPy/scikit-learn: Use the GitHub search API to look through the code base for any case-insensitive appearance of the string "scikit" or "sklearn" where `sklearn` is the name of the library the must be imported to use the popular machine learning libary, scikit-learn
- TensorFlow: Use the GitHub search API to look through the code base for any case-insensitive appearance of the string "tensorflow"
- PyTorch: Use the GitHub search API to look through the code base for any case-insensitive appearance of the string "pytorch"
- MATLAB: Use the GitHub repository `languages` API to determine what languages are used in the repository, returning a positive response if MATLAB is found in the list of languages used

After I figure out the tools used in each specific paper's code, I'm able to then aggregate them by the proceeding by looking through each of the results found above and then bucketing them in a Python dictionary by proceeding.

## Architecture and Design Considerations

### Get Paper Information and Update DB Flow

1. First, the information on the Papers With Code are pulled and decompressed from the Papers With Code website automatically.
2. We use this data to build a Python dictionary called `paper_data_dict` of the abstract_url to some data on the paper:

```
    abstract_url: {
	    "paper_title",
	    "paper_arxiv_id",
	    "paper_url_abs",
	    "paper_url_pdf",
	    "repo_url",
	    "mentioned_in_paper",
	    "mentioned_in_github",
	    "proceeding",
    }
```

3. We then go through each of the papers stored in `paper_data_dict` and run the following steps:
   1. Create a `PaperWithCode` abstraction which stores info on the paper and contains a `GitHubRepo` abstraction which acts as a connector to the GitHub API. We'll need this to identify our ML tools.
   2. Run all the `BasePaperWithCodePlugin` logic we pass to the `PaperWithCode` plugin function. This populates the `PaperWithCode` class with the results of the heuristics we ran to determine what ML libraries are used in the code.
   3. Save the new `PaperWithCode` information with the detected ML tools to a pickleDB file, a text file based database.
4. At this point, we'll have run all our heuristics and we have stored all the papers along with the corresponding ML tools that are used. Now we can go through each element and bucket them by proceeding and output the results when desired.

### Getting Papers With Code Data

In order to reduce the amount of manual work required to set this up, the code base will automatically pull the Papers With Code data-sets ["Papers with abstracts"](https://paperswithcode.com/media/about/papers-with-abstracts.json.gz) and ["Links between papers and code"]("https://paperswithcode.com/media/about/links-between-papers-and-code.json.gz") from hard-coded web addresses. The reason we need both data-sets is because the proceeding information is held in the "Papers with abstracts" data-set and the GitHub link is held in the "Links between papers and code" data-set. These two data-sets share a number of fields that we can link them together by, but we will use the "url_abs"/"paper_url_abs" to join the data-sets since these should be unique per paper and we want our final output to contain this field.

### Core Abstractions

- **CachedData**: Basic caching structure that pulls data only if it doesn't already exist in the current runtime. We use this to reduce our API calls.
- **GitHubRepo**: Helps us keep track of information that we have on a particular GitHub repository. This abstraction is initialized with a web address that points to a GitHub repository and it holds the address, repository name, as well as the GitHub API SDK object that allows us to make queries to the API. We also do some caching of repository data here when possible, so if multiple plugins require the same details, we don't need to make additional API calls. Right now the only information we store and cache are the languages that the repository uses since we require this for the MATLAB plugin, however, if you find that there are other GitHub repository properties that are required to build additional plugins, you would want to query for them and cache them in this class.
- **PaperWithCode**: Holds information on a single Paper With Code paper including the address to the paper's abstract as well as the relevant GitHubRepo object. This abstraction is initialized with a Python dictionary value that was built in the previous "Getting Papers With Code Data" step. The abstraction takes care of automatically initializing the GitHub API SDK object which validates and allows you to query the GitHub API. This abstraction has two important methods, `apply_plugins` and `serialize` where `apply_plugins` allows you to apply a list of `BasePaperWithCodePlugin` abstractions to help identify what ML tools are used the by the code and `serialize` allows us to store the `PaperWithCode` abstraction in a text format that can be used to rebuild the object if needed.
- **BasePaperWithCodePlugin**: Defines a shapes for custom plugins to be written where a plugin is a class that contains a variable, `plugin_key`, to help with identifying the tool found on output and a method, `apply`, which applies a heuristic to the PaperWithCode and returns `True` or `False` based on if the heuristic was met or not.

### Notable Trade-offs and Considerations

- **Plugin-Style Architecture**: I decided to implement this in a way where the actual heuristics and the pulling of data are separated and kept in separate files and directories. What this enables is the independent building of plugins and heuristics and the pulling of information. There would need to be some sort of communication between the different teams if the heuristics teams need new information about the paper to write good plugins, but this does increase isolation. This also makes it easy to do things like test heuristics and data processing separately.
- **GitHub API Rate Limit**: This was one of the biggest issues I ran into. I found that I couldn't hit the API very many times in quick succession to pull information about the code. This is what prompted me to use some sort of persistent storage, PickleDB, to save whatever results I already got. PickleDB is not ACID, so I wrote my code in a way so that there would be no database entry inserted if the operation was not completely successful. This way, every time I run the code, I can look at PickleDB to determine what I already have data for and skip that entry. This also means that my code had to be run over different periods of time to wait out the rate limit. Some ideas I would try to implement if I had more time would be API key/account rotation, site scraping, or cloning the repositories instead of using various API features.
- **Concurrency**: Something I also attempted, before I ran into the API rate limit, is using the Python `asyncio` and `concurrent` libraries in order to set off multiple requests at once. This would have worked since we can look at different GitHub repositories independently of each other and still get the results we wanted. I ended up getting some code running to use 20 workers at a time, but later found out this won't fly because of the GitHub API rate limit. One way we could work around this is to have different requests use different API keys at a pace that respects the rate limit and then we could work `n` times faster than the given rate limit if we had `n` different API keys to use.
- **Heuristics and Plugins**: For the plugins, I pursued heuristics that are pretty basic and could run into false positive cases. For example, a lot of my heuristics rely on GitHub search. If I search for something like "numpy", it might appear only in the README or some other documentation and not actually in the code. The `numpy` heuristic that I used would actually return a false positive in this case. There are other things we could do to improve the heuristics if we wanted to make it more perfect by looking only at the code and non-comment lines. I originally was hoping to rely on Python package etiquette like the `requirements.txt` file, but quickly realized that many of these repositories didn't have the same shape or structure.
- **Performance**: It takes a long time to run `update_db` since my code is currently bounded by the GitHub API rate limit, but since I store the results of `update_db`, running `show_tools`, `show_proceeding_tools`, and `show_proceeding_tools_percentage` will run significantly faster and uses all local data. The amount of time it takes me to run `update_db` is something like 5 minutes for every 6 papers. There are 20000 or so papers in the archive, which would require something like 12 days in order to get all the heuristics for all the papers. This can be significantly improved if I can successfully implement some of the rate limiting mitigation strategies I mentioned.
- **Testing**: I wrote a single test only since it's really getting late where I am right now and the test is in the root directory since I didn't want to deal with setting up a testing framework that supported test discovery and other fancy features.
- **Making the Code Production-Ready**: There are a number of things I would improve if we were working in a large codebase and I was looking to make this production-ready.
  _ Add more unit tests for better unit-test coverage using a robust framework with test discovery, like `pytest`. Improve unit-test-ability of code, particularly in classes that use the GitHub API. To do this, I would use some sort of tool that allows you to mock responses and try to split up and isolate the API logic as much as possible so that I can nicely test the API response processing logic.
  _ Figure out how to speed up the run-time of `update_db` or decide that it is OK for it to run that long and set up the job somewhere where we can keep it running and is easily traceable like in Jenkins or Airflow hosted on a remote box.
  _ Fix the way that things are imported by defining Python packages in my directories.
  _ Better CLI interface using some sort of robust CLI framework like `argparse` or `click`. \* Think about who is going to be primarily using this tool. If it's going to be more non-technical folks, probably consider building some sort of UI to manage the data. If someone is actually going to use this to look for papers and code, build additional functionality to do things like filter papers by an ML tool and filter proceedings by an ML tool.

## Usage Instructions and Examples

### Setup

_Setup instructions will be for a Ubuntu machine. I don't have another computer to test other setup instructions._

First, make sure you have Python3 and pip3 installed:

```
sudo apt-get install python3
sudo apt-get install python3-pip
```

Then, install the requirements from the home directory of the project:

```
pip3 install -r requirements.txt
```

### CLI Usage

All commands should be run from the home directory of the project where `main.py` is located.

- `python3 main.py update_db`
  - Pulls new information from Papers With Code and adds new papers to DB.
  - This command will make API calls with my GitHub API key and modify the DB file.
- `python3 main.py show_tools`
  - Shows the unique tools for each paper in the format: `abstract_url: tool1, tool2, tool3`
- `python3 main.py show_proceeding_tools`
  - Shows the unique tools for each proceeding in the format: `proceeding: tool1, tool2, tool3`
- `python3 main.py show_proceeding_tools_percentage`
  - Shows the popularity of individual tools for each proceeding in the format:

```
           {
               proceeding: {
                   tool1: amount - percentage,
                   tool2: amount - percentage,
                   tool3: amount - percentage,
               }
           }
```

### Unit Testing

There's only one test here. I intended to re-work the code to make it most unit testable and to write more comprehensive unit tests, but I'm trying to keep the amount of time I spend on this bounded and it's really getting late. In a production situation, this would be pretty important to complete before launching.

- `python3 test.py`
  - Runs my single sanity check style unit test for the `CachedData` model
