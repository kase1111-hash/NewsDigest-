"""Main CLI application for NewsDigest."""

import click

from newsdigest.version import __version__


@click.group()
@click.version_option(version=__version__, prog_name="newsdigest")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """NewsDigest - Semantic compression engine for news.

    Extract signal from noise. Your 4-hour news habit, compressed to 5 minutes.
    """
    ctx.ensure_object(dict)


# Import and register commands
# These will be implemented in their respective modules
# from newsdigest.cli.extract import extract
# from newsdigest.cli.compare import compare
# from newsdigest.cli.stats import stats
# from newsdigest.cli.digest import digest
# from newsdigest.cli.sources import sources
# from newsdigest.cli.watch import watch
# from newsdigest.cli.analytics import analytics
# from newsdigest.cli.setup import setup_cmd


if __name__ == "__main__":
    cli()
