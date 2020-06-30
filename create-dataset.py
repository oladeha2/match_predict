import click
import subprocess


def scrape_results():
    subprocess.run(['/bin/bash', './scripts/scrape_results.sh'])


def scrape_ratings():
    subprocess.run(['/bin/bash', './scripts/scrape_ratings.sh'])


command_dict = {
    "results": scrape_results,
    "ratings": scrape_ratings
}


def validate_args(args):
    if len(args) < 1 or len(args) > 2:
        raise click.BadParameter('There should be at least one argument for --data and no more than 2')
    for arg in args:
        if arg not in command_dict.keys():
            raise click.BadParameter("--data must be one of \"results\" or \"ratings\"")


@click.command()
@click.option('--data', '-d', multiple=True, help="Data option for the dataset you would like to be scraped and saved")
def create_data(data):
    """
        Mini CLI for selecting which dataset you would like to download (results, ratings or both)
    """
    validate_args(data)
    for dataset in data:
        print("-"*100)
        command_dict[dataset]()
        print("-"*100)


if __name__ == "__main__":
    create_data()
