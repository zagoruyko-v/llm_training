import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from app.services.llm_service import LLMService, Message

app = typer.Typer()
console = Console()
llm_service = LLMService()


@app.command()
def chat(
    model: Optional[str] = typer.Option(None, help="Model to use"),
    temperature: Optional[float] = typer.Option(
        None, help="Temperature for generation"
    ),
    system_prompt: Optional[str] = typer.Option(None, help="System prompt to use"),
):
    """Start an interactive chat session with the LLM."""
    console.print(Panel.fit("Welcome to the LLM Chat Interface!", style="bold blue"))

    context = []
    if system_prompt:
        context.append(Message(role="system", content=system_prompt))

    while True:
        user_input = Prompt.ask("\n[bold green]You[/bold green]")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            result = llm_service.generate_response(
                prompt=user_input, model=model, temperature=temperature, context=context
            )

            response = result["message"]["content"]
            context.append(Message(role="user", content=user_input))
            context.append(Message(role="assistant", content=response))

            console.print(f"\n[bold blue]Assistant[/bold blue]: {response}")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")


@app.command()
def list_models():
    """List all available models."""
    try:
        models = llm_service.list_models()
        console.print("\n[bold]Available Models:[/bold]")
        for model in models:
            console.print(f"• {model}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@app.command()
def pull_model(model_name: str):
    """Pull a model from Ollama's model library."""
    try:
        console.print(f"Pulling model {model_name}...")
        result = llm_service.pull_model(model_name)
        console.print("[bold green]Model pulled successfully![/bold green]")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


if __name__ == "__main__":
    app()
