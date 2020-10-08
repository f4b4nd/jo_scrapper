import os
import re
import sympy
from requests import Session
from lxml.html import fromstring
from lxml import etree
import pathlib
from journalofficiel.alerts import Alert
from journalofficiel.savefile import SaveFile


class JOScraper:

    def __init__(self):
        self.ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
        self.session = Session()

    def filename(self, date):
        y_m_d = date.strftime(r'%Y_%m_%d')
        return f"{y_m_d}.pdf"
    
    def dirpath(self, doc):
        return self.ROOT_DIR / "pdf" / doc

    def captcha_solver(self, captcha):

        def captcha_to_equation(captcha):
            equation = re.sub(r'[a-z]{3}\-[a-z]{4}|[a-z]+', chars2int,
                              captcha)
            equation = insert_unknow(equation)
            return equation

        def chars2int(match):
            chars2int = {
                'un': '1', 'deux': '2', 'trois': '3', 'quatre': '4',
                'cinq': '5', 'six': '6', 'sept': '7', 'huit': '8', 'neuf': '9',
                'dix': '10', 'onze': '11', 'douze': '12', 'treize': '13',
                'quatorze': '14', 'quinze': '15', 'seize': '16',
                'dix-sept': '17',  'dix-huit': '18', 'dix-neuf': '19',
            }
            return chars2int[match.group(0)]

        def insert_unknow(equation):
            equation = re.findall(r'\+|\-|\=|\d{1,2}', equation)
            equation.insert(unknown_position(equation), 'x')
            equation[3] = '-'
            equation = "".join(equation)
            return equation

        def unknown_position(equation):
            if equation[-1] == '=':
                return 4
            elif equation[0] in ['+', '-']:
                return 0
            elif equation[1] in ['+', '-']:
                return 2

        equation = captcha_to_equation(captcha)
        result = sympy.solve(equation)[0]
        print('Captcha:', captcha, '-> Result:', result, end=" ")

        return result

    def run(self, date, doc):

        hostname = 'https://www.legifrance.gouv.fr'
        label = {'Decrets': 'portant changements de noms',
                 'Demandes': 'Demandes de changement'}
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        
        def data_is_available(date, doc):
            """
            TODO: aim url looking like:
                - www.legifrance.gouv.fr/jorf/jo/2020/10/6/0243
                - www.legifrance.gouv.fr/eli/jo/2020/10/6/0243
            PB: webpage content is generated with javascript -> Need to use Selenium ? (w/ chrome headless mode)
            """
            date = date.strftime(r'%Y/%m/%d')
            r = self.session.post(url=f"{hostname}/jorf/jo/{date}/0244", headers=headers) 
            web_page = fromstring(r.content)
            print(etree.tostring(web_page))
            a_tags = web_page.xpath(f"//a")
            print(f"{hostname}/jorf/jo/{date}/")
            a_tags = [ str(etree.tostring(a_tags[i])) for i, x in enumerate(a_tags)]
            print("\n".join(a_tags))
            a_contains = web_page.xpath(f"//a[contains(text(), '{label[doc]}')]")
            
            if links == []:
                return False
            else:
                endpoint = links[0].attrib['href']
          
                update_request(r, endpoint)
                return True

        def get_data(r, endpoint):
            r = self.session.post(url=f"{hostname}/{endpoint}", cookies=r.cookies)
            web_page = fromstring(r.content)
            links = web_page.xpath("//a[contains(text(), "
                                  "\"Accéder à l'espace protégé\")]")
            endpoint = links[0].attrib['href']

            update_request(r, endpoint)
            captcha = get_captcha(self.r, self.endpoint)
            post_captcha_payload(self.r, self.endpoint,
                                 self.captcha_solver(captcha))
            return self.r.content

        def get_captcha(r, endpoint):
            r = self.session.post(url=f"{hostname}/{endpoint}", cookies=r.cookies)
            web_page = fromstring(r.content)
            captcha = web_page.xpath("//input[@name='captcha']/../text()")
            captcha = "".join(captcha)
            captcha = re.sub(r"\t|\n|\r|\s+", "", captcha)
            return captcha

        def post_captcha_payload(r, endpoint, payload):
            r = self.session.post(url=f"{hostname}/{endpoint}",
                             data={'captcha': payload,
                                   'bouton': 'Soumettre la réponse'},
                             cookies=r.cookies)
            r = self.session.post(url=f"{hostname}/jo_pdf.do?inap",
                             cookies=r.cookies)
            r = self.session.post(url=f"{hostname}/jo_pdf_frame.do?dl",
                             cookies=r.cookies)
            update_request(r)

        def update_request(r, endpoint=None):
            self.r = r
            if endpoint is not None:
                self.endpoint = endpoint

        if data_is_available(date, doc):
            content = get_data(self.r, self.endpoint)
            save_file = SaveFile(self.dirpath(doc), self.filename(date), content)
            save_file.run()
        else:
            alert = Alert(date.strftime(r"%d/%m/%Y"))
            alert.run("no_data")
