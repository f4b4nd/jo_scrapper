from journalofficiel.scraper import JOScraper
import argparse
import datetime as dt
import pendulum as pnd


def period(start, end) -> list:
    d1, m1, y1 = start.split("/")
    d2, m2, y2 = end.split("/")
    start = pnd.datetime(int(y1), int(m1), int(d1))
    end = pnd.datetime(int(y2), int(m2), int(d2))
    dates = pnd.period(start, end)
    return dates


def today():
  today = dt.date.today()
  return today.strftime("%d/%m/%Y")


parser = argparse.ArgumentParser()
parser.add_argument("start", help="starting date in DD/MM/YYYY", type=str)
parser.add_argument("--end", default=today(),
                    help="ending date in DD/MM/YYYY", type=str)
parser.add_argument("--doc", default='Decrets',
                    choices=['Decrets', 'Demandes'], type=str)
args = parser.parse_args()


if __name__ == '__main__':

    jo_scraper = JOScraper()
    for date in period(args.start, args.end):
        jo_scraper.run(date, args.doc)
