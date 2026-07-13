from pathlib import Path
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.agents import create_agent


load_dotenv()

PROMPT_PATH = Path("prompt.txt")

with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

from agent.tools import (
    check_order_status,
    check_inventory,
    verify_vip,
    check_branch_open_now,
    find_product_in_other_branches,

)


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3
)


agent = create_agent(
    model=llm,
    tools=[
        check_order_status,
        check_inventory,
        verify_vip,
        check_branch_open_now,
        find_product_in_other_branches,

    ],
    system_prompt=SYSTEM_PROMPT
)