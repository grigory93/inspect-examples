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

## Docker Network "Address Pools Fully Subnetted" Error

**Error:** `Error response from daemon: all predefined address pools have been fully subnetted`

**Cause:**
This error occurs when Docker runs out of available subnets for creating new networks. This typically happens because:
1.  **Orphaned Networks:** Interrupted `inspect_ai` runs leave behind networks and containers that are not cleaned up.
2.  **High Concurrency:** Running many evaluations in parallel creates more networks than the default Docker configuration allows (limit is ~31 networks).

### Solution 1: Clean Up (Immediate Fix)

Remove all orphaned containers and networks:

```bash
# Stop and remove all inspect-gaia containers
docker ps -a --filter "name=inspect-gaia" --format "{{.ID}}" | xargs docker stop
docker ps -a --filter "name=inspect-gaia" --format "{{.ID}}" | xargs docker rm

# Prune unused networks
docker network prune -f
```

### Solution 2: Configure Docker (Permanent Fix)

Configure Docker to support more networks by using smaller subnets (`/24` instead of the default).

1.  Edit or create `~/.docker/daemon.json` (Linux/macOS) or `%programdata%\docker\config\daemon.json` (Windows):

    ```json
    {
      "default-address-pools": [
        {
          "base": "10.0.0.0/8",
          "size": 24
        }
      ]
    }
    ```

2.  **Restart Docker Desktop** or the Docker daemon for changes to take effect.

### Solution 3: Reduce Concurrency

Limit the number of parallel evaluations in your `eval_set` call:

```python
eval_set(..., max_samples=10)
```

## Anthropic Model Names

To see available Anthropic models run command:
```
curl https://api.anthropic.com/v1/models \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"
```