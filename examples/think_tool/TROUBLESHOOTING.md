# Troubleshooting

## Environment

### RAGChecker package incompatibility with anthropic

Incompatible with RAGChecker: remove ragchecker dependency: current version of the pyproject.toml has ragchecker dependency removed.

### Building inpsect-evals locally

Added the following to pyproject.toml to successfully build with the dev version of inspect-evals package:
```
[tool.hatch.metadata]
allow-direct-references = true
```

## GAIA Dataset download fix

Upon running the GAIA task, it will attempt to download the dataset from the HuggingFace hub. For this to work, you will need to gain access to the dataset (by filling out a form on the GAIA huggingface repository), and also create and set an access token. You will need to define the HF_TOKEN environment variable to access the dataset:

```
HF_TOKEN=<hf-token>
```

At the time of writing the lastest available version of inpsect-evals on Pypi contained a bug preventing downloading GAIA dataset.

See PR https://github.com/UKGovernmentBEIS/inspect_evals/pull/660 for the bug and the fix.
Solved by changing pyproject.toml to use the latest version of insepct-evals from github where the problem was fixed.
Necessary to remove cache files by following both the the PR notes and the error message printing exact location of the files on the local system.
