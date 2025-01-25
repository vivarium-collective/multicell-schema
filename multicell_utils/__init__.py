import pprint


pretty = pprint.PrettyPrinter(indent=2)


def pf(x):
    """Format ``x`` for display."""
    return pretty.pformat(x)