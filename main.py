from journalofficiel.scraper import JOScraper
import argparse
import datetime as dt

def add_current_year(date) -> dt.datetime:
    year = dt.date.today().strftime('%Y')
    date = dt.datetime.strptime(date, r"%d/%m")
    return date.replace(year=int(year))
     

def dates(start: str, end: str) -> list:
    try:
        start = dt.datetime.strptime(start, r"%d/%m/%Y")
    except ValueError:
        start = add_current_year(start)
        
    end = dt.datetime.strptime(end, r"%d/%m/%Y")
    delta = end - start
    dates = [start + dt.timedelta(days=i) for i in range(delta.days+1)]
    return dates


def today():
  today = dt.date.today()
  return today.strftime(r"%d/%m/%Y")


parser = argparse.ArgumentParser()
parser.add_argument("start", help="starting date in DD/MM/YYYY, or DD/MM for current year", type=str)
parser.add_argument("--end", default=today(),
                    help="ending date in DD/MM/YYYY", type=str)
parser.add_argument("--doc", default='Decrets',
                    choices=['Decrets', 'Demandes'], type=str)
args = parser.parse_args()


if __name__ == '__main__':

    jo_scraper = JOScraper()
    for date in dates(args.start, args.end):
        jo_scraper.run(date, args.doc)
