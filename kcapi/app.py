import os.path

import click
import yaml
from click_default_group import DefaultGroup

from kcapi.connector import KCConnector
from kcapi.data_processor import DataProcessor
from kcapi.trailer import Trailer
from kcapi.util import init_logger, to_date, date_to_str, utcnowloc


def init_config(config_filename):
    with open(config_filename) as f:
        conf = yaml.safe_load(f)
        init_logger(conf.get('log_level'))
        return conf


@click.group(cls=DefaultGroup, default='run', default_if_no_args=True, help="Spypy help text")
@click.pass_context
def cli(ctx):
    ctx.obj = {'help': ctx.get_help()}


@cli.command(help="")
@click.pass_context
@click.option('-c', '--config-filename', default='config.yaml', type=str)
def sell_trail(ctx, config_filename):
    cfg = init_config(config_filename)

    trailer = Trailer(cfg).run()


@cli.command(help="Write some test images")
@click.pass_context
@click.option('-c', '--config-filename', default='config.yaml', type=str)
def download_history(ctx, config_filename):
    cfg = init_config(config_filename)

    conn = KCConnector(**cfg)

    start = to_date(cfg['start_date'])
    end = to_date(cfg.get('end_date')) if cfg.get('end_date') else utcnowloc()
    root = os.path.dirname(config_filename)
    folder = os.path.join(root, "output_{}_to_{}".format(date_to_str(start), date_to_str(end)))

    orders = conn.get_orders(start, end, cfg.get('pair'))
    d = DataProcessor(orders)
    d_by_pair = d.sort_by_pair()
    summary = d.summarize_pairs(d_by_pair)

    d.to_csv_summary(summary, folder=folder)
    d.to_csv_pairs(d_by_pair, folder=folder)

    pass


if __name__ == '__main__':
    cli()
