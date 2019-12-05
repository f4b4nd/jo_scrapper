from journalofficiel.scraper import JOScraper
import argparse
import datetime as dt

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

    jo_scraper = JOScraper(args.start, args.end)
    for date in jo_scraper.period():
        jo_scraper.run(date, args.doc)
