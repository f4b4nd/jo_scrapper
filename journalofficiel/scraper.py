import os
import re
import sympy
from datetime import datetime as dt
from requests import Session
import pendulum as pnd
from lxml.html import fromstring
import pathlib


class JOScraper:

    def __init__(self, start, end):
        self.ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
        self.start = start
        self.end = end
        
    def period(self):
        d1, m1, y1 = self.start.split("/")
        d2, m2, y2 = self.end.split("/")
        start = pnd.datetime(int(y1), int(m1), int(d1))
        end = pnd.datetime(int(y2), int(m2), int(d2))
        dates = pnd.period(start, end)
        return [dt.strftime(x, r'%Y/%#m/%#d') for x in dates.range('days')]

    def filename(self, date):
        y_m_d = self.d8format(date)["y_m_d"]
        return f"{y_m_d}.pdf"
    
    def dirpath(self, doc):
        return self.ROOT_DIR / "pdf" / doc
        
    def d8format(self, date):
        d8 = dt.strptime(date, r'%Y/%m/%d')
        ddmmyy = d8.strftime(r'%d/%m/%Y')
        y_m_d = d8.strftime(r'%Y_%m_%d')
        return {"d/m/y": ddmmyy, "y_m_d": y_m_d}

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

        session = Session()

        def data_is_available(date, doc):
            r = session.post(url=f"{hostname}/eli/jo/{date}/")
            web_page = fromstring(r.content)
            links = web_page.xpath(f"//a[contains(text(), '{label[doc]}')]")

            if links == []:
                return False
            else:
                endpoint = links[0].attrib['href']
                update_request(r, endpoint)
                return True

        def get_data(r, endpoint):
            r = session.post(url=f"{hostname}/{endpoint}", cookies=r.cookies)
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
            r = session.post(url=f"{hostname}/{endpoint}", cookies=r.cookies)
            web_page = fromstring(r.content)
            captcha = web_page.xpath("//input[@name='captcha']/../text()")
            captcha = "".join(captcha)
            captcha = re.sub(r"\t|\n|\r|\s+", "", captcha)
            return captcha

        def post_captcha_payload(r, endpoint, payload):
            r = session.post(url=f"{hostname}/{endpoint}",
                             data={'captcha': payload,
                                   'bouton': 'Soumettre la réponse'},
                             cookies=r.cookies)
            r = session.post(url=f"{hostname}/jo_pdf.do?inap",
                             cookies=r.cookies)
            r = session.post(url=f"{hostname}/jo_pdf_frame.do?dl",
                             cookies=r.cookies)
            update_request(r)

        def update_request(r, endpoint=None):
            self.r = r
            if endpoint is not None:
                self.endpoint = endpoint

        if data_is_available(date, doc):
            content = get_data(self.r, self.endpoint)
            save_pdf = SavePDF(self.dirpath(doc), self.filename(date), content)
            save_pdf.run()
        else:
            alert = Alert(date)
            alert.run("no_data")

            
class SavePDF:
    
    def __init__(self, dirpath, filename, content):
        self.dirpath = dirpath
        self.filename = filename
        self.content = content
        self.filepath = dirpath / filename
        
    @staticmethod
    def create_dir(dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            print("# New directory created", end=" ")
    
    @staticmethod
    def file_exist(filepath):
        return os.path.exist(filepath)
    
    def run(self):
        
        self.create_dir(self.dirpath)
   
        alert = Alert(self.filename)
        
        if not self.file_exists(self.filepath):
            open(self.filepath, 'wb').write(self.content)
            alert.run("success")
        else:
            alert.run("already_exists")
            
            
class Alert:
    
    def __init__(self, ddmmyy):
        self.ddmmyy = ddmmyy
        
    def run(self, status):
        alerts = {
            "success": f"# New file created for {self.ddmmyy}! ",
            "already_exists": f"# File already exists for {self.ddmmyy}",
            "no_data": f"No data on {self.ddmmyy}",
        }
        status = alerts[status] if status in alerts else ""
        print(status)
 
