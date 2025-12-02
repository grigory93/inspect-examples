from inspect_ai import eval_set
from inspect_evals.gaia import gaia_level1, gaia_level2
from inspect_ai.log import list_eval_logs, read_eval_log
from inspect_ai.solver import Solver, basic_agent, system_message
from inspect_ai.tool import bash, python, think, web_browser, web_search
from inspect_ai.util._sandbox.environment import SandboxEnvironmentType
from textwrap import dedent

from inspect_evals.gaia.gaia import default_solver


think_prompt = dedent("""
            Use the think tool to think about something. It will not obtain
            new information or make any changes to the repository, but just 
            log the thought. Use it when complex reasoning or brainstorming
            is needed. For example, if you explore the repo and discover
            the source of a bug, call this tool to brainstorm several unique
            ways of fixing the bug, and assess which change(s) are likely to 
            be simplest and most effective. Alternatively, if you receive
            some test results, call this tool to brainstorm ways to fix the
            failing tests.
        """)

gaia_system_prompt = dedent("""
        You are an autonomous AI agent, consisting of a large language model and a scaffolding program that runs on a linux VM.

        You have full control over your VM through the scaffolding program's provided functions, including: writing and editing files, running bash commands, installing packages etc.. From your VM, you can access the internet.

        You are state-of-the-art, and excellent at analysis, planning and programming. You possess encyclopedic knowledge of the world. You write in a very direct and concise style.

        You are resourceful and adaptive, and you never give up. Before deciding something can't be done, you try it out. You consider multiple options and choose the best one. If your current approach doesn't work, you formulate a new plan. You are given a task you need to solve completely on your own.

        Use the think tool to think about the task and the tools available. It will not obtain
        new information or make any changes to the repository, but just log the thought. Use it when complex reasoning or brainstorming is needed before calling other tools. 
        For example use think tool to:
        - if you explore the resource (link) and find some information that appears relevant, analyze with think tool its utility and relevance to the task and how it can be used to lead to next steps in solving the task.
        - if you receive some intermediate results, call think tool to brainstorm ways to analyze the results and how to use them in the next steps with the tool calls available.
        - if you find some information that can be used to achieve the goal of the task, call think tool to brainstorm ways to utilize the new information to achive the goal of the task. 
        Note that think tool will not obtain new information or make any changes to the repository, but just log the thought.

        When you are ready to answer, use the submit tool to provide your final answer.
        """
            )

def gaia_solver_with_think(
    max_attempts: int, max_messages: int, code_timeout: int = 180
) -> Solver:
    return basic_agent(
        init=system_message(
            gaia_system_prompt
        ),
        tools=[
            bash(code_timeout), 
            python(code_timeout), 
            think(description=think_prompt),
        ] + web_browser(),
        max_attempts=max_attempts,
        max_messages=max_messages,
    )

models = [
    # "openai/gpt-5-nano",
    # "openai/gpt-5-mini",
    # "openai/gpt-4o-mini",
    # "openai/gpt-4.1-mini",
    # "anthropic/claude-sonnet-4-5",
    # "anthropic/claude-haiku-4-5",
    # "anthropic/claude-sonnet-4-20250514",
    # "anthropic/claude-3-5-haiku-20241022",
    "mistral/mistral-small-latest",
    "mistral/mistral-medium-latest",
]

# curent run config
config_run_eval = True
config_eval_limit = 50
config_eval_max_samples = 10
config_gaia_benchmark = gaia_level1
config_gaia_solver = default_solver
config_gaia_solver = gaia_solver_with_think
config_gaia_sandbox = ("docker", "examples/think_tool/compose.yaml")
config_log_dir = f'./logs_mistral10_{config_gaia_benchmark.__name__}_{config_eval_limit}_{"think" if config_gaia_solver == gaia_solver_with_think else "default"}'


# Run
if config_run_eval is True:
    success, gaia_logs = eval_set(
        [config_gaia_benchmark(
            solver=config_gaia_solver(max_attempts=1, max_messages=100),
            sandbox=config_gaia_sandbox)
        ], 
        model=models, 
        log_dir=config_log_dir, 
        limit=config_eval_limit,
        max_samples=config_eval_max_samples,
    )

    print(success)

else:
    gaia_logs = []
    for eval_log_info in list_eval_logs(log_dir=config_log_dir):
        log = read_eval_log(eval_log_info)
        gaia_logs.append(log)

