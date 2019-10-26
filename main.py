from journalofficielscraper import JOScraper

if __name__ == '__main__':

    start = input('Enter starting date in DD/MM/YYYY: ')
    end = input('Enter ending date in DD/MM/YYYY: ')

    jo_scraper = JOScraper(start, end)
    for date in jo_scraper.dates():
        jo_scraper.run(date, 'Décrets')
