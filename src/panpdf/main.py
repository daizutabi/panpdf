import typer

app = typer.Typer()


@app.command()
def hello(name: str):
    typer.echo(name)


def cli():
    app()
