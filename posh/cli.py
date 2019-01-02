# -*- coding: utf-8 -*-

"""Console script for posh."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for posh."""
    click.echo("Replace this message by putting your code into "
               "posh.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
