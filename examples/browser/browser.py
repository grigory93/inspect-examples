from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes, model_graded_qa
from inspect_ai.solver import generate, use_tools
from inspect_ai.tool import web_browser
# Define the dataset globally for clarity and reusability
EVAL_SAMPLES = [
    Sample(
        id="aisi_gov_uk_uk_government",
        input="Use the web browser tool to navigate to https://www.aisi.gov.uk/. Then, see if you can find a page on the site that to find out if the UK AISI belongs to the UK government. Simply answer with 'Yes' or 'No'.",
        target="Yes"
    ),
    Sample(
        id="aisi_gov_uk_controlarena",
        input="Use the web browser tool to navigate to https://www.aisi.gov.uk/. Then, see if you can find a page on the site that describes what ControlArena is. Answer with the definition in one sentence.",
        target="ControlArena is a library for running AI control experiments."
    ),
    Sample(
        id="aisi_gov_uk_inspect_sandboxing_toolkit",
        input="Use the web browser tool to navigate to https://www.aisi.gov.uk/. Then, see if you can navigate to a page with the definition of the Inspect Sandboxing Toolkit. Answer with the extended definition in one rather long sentence.",
        target="The Inspect Sandboxing Toolkit is a set of plugins built and open-sourced to accommodate a variety of agentic evaluation environments for advanced AI models, along with documentation on how to approach choosing a sandbox."
    )
]


@task
def browser():
    return Task(
        dataset=EVAL_SAMPLES,
        solver=[
            use_tools(web_browser()),
            generate(),
        ],
        message_limit=10,
        working_limit=3 * 60,
        token_limit=(1024*500),
        scorer=model_graded_qa(model="openai/gpt-4o"),
        sandbox=("docker", "compose.yaml"),
    )