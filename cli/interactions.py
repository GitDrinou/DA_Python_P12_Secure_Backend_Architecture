import click


def prompt_if_missing(value, label, **kwargs):
    if value is not None:
        return value
    return click.prompt(label, **kwargs)


def confirm_if_requested(value, prompt_text):
    if value:
        return
    confirmed = click.confirm(prompt_text, default=False)
    if not confirmed:
        raise click.Abort()
