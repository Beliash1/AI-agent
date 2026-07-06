"""
mcp/client.py — MCP (Model Context Protocol) სერვერებთან დაკავშირების სტარტერი.

(გადმოტანილია repo root-იდან backend/mcp/-ში, რომ დანარჩენ კოდთან ერთად
ერთნაირი import-კონვენციით მუშაობდეს — ადრე top-level mcp/ საერთოდ
არსად არ იყო იმპორტირებული, ანუ მკვდარი კოდი იყო.)

ᲛᲜᲘᲨᲕᲜᲔᲚᲝᲕᲐᲜᲘ: ეს ფაილი ᲐᲠ არის სრულად მზა ინტეგრაცია — MCP სერვერები
(GitHub, Slack, Google Drive და ა.შ.) ცალ-ცალკე დაყენებას/კონფიგურაციას
საჭიროებენ (ხშირად API key/OAuth). ეს არის ჩონჩხი, რომელსაც შენს
კონკრეტულ სერვერებზე მორგებ.

დამოკიდებულება: pip install mcp --break-system-packages
"""

from dataclasses import dataclass


@dataclass
class MCPServerConfig:
    name: str
    command: str          # მაგ: "npx"
    args: list[str]        # მაგ: ["-y", "@modelcontextprotocol/server-github"]
    env: dict | None = None  # მაგ: {"GITHUB_TOKEN": "..."}


# შენი MCP სერვერების სია — შეავსე რეალური მონაცემებით
MCP_SERVERS: list[MCPServerConfig] = [
    # მაგალითი (გააქტიურებამდე კომენტარი მოხსენი და API key ჩასვი):
    # MCPServerConfig(
    #     name="github",
    #     command="npx",
    #     args=["-y", "@modelcontextprotocol/server-github"],
    #     env={"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"},
    # ),
]


async def list_available_tools(server: MCPServerConfig) -> list[dict]:
    """
    დაუკავშირდება კონკრეტულ MCP სერვერს და დააბრუნებს მის tool-ების სიას.
    რეალურად სამუშაოდ სჭირდება `mcp` პაკეტის კლიენტის სესია (stdio ან SSE).

    ეს ფუნქცია სტუბია — რეალური კავშირისთვის საჭიროა:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    და server.command/args-ის მიხედვით სესიის გახსნა.
    """
    raise NotImplementedError(
        f"'{server.name}' სერვერთან რეალური დაკავშირება ჯერ არ არის ჩართული. "
        "დაამატე mcp პაკეტის კლიენტის კოდი აქ, სერვერის დოკუმენტაციის მიხედვით."
    )


def get_configured_servers() -> list[MCPServerConfig]:
    """აბრუნებს ყველა კონფიგურირებულ სერვერს (ცარიელია, სანამ MCP_SERVERS არ შეავსებ)."""
    return MCP_SERVERS
