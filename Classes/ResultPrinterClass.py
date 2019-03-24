from Classes.DBHandlerClass import session_scope, Vacancies, Platform
from config import ROOT_DIR
import os


class ResultPrinter:

    def __init__(self, dbms, browser):
        self.header = '---- # (ResultPrinter)'
        self.dbms = dbms
        self.browser = browser
        self.vacancy_template = "<li>{}</li>"

    def print_result_to_html(self, search_type, open_html_after_finish: bool = True):
        html_result_file_name = 'result.html'
        html_result_file_path = ROOT_DIR + '/' + html_result_file_name

        with open(html_result_file_path, 'w') as html_file:
            html_file.write(f'<html><body><h1>Search Type: {search_type}</h1>\n')

            with session_scope(dbms=self.dbms) as session:
                # Get all platform names
                platform_names = []
                result_rows = session.query(Platform.name).all()

                for row in result_rows:
                    platform_names.extend(list(row))

                print(platform_names)

                for platform in platform_names:
                    html_file.write(f'<h2>{platform}</h1>')
                    html_file.write('<ul>')

                    # Get all entries in database for this platform
                    result_rows = session.query(Vacancies)\
                        .filter(Vacancies.platform == platform, Vacancies.search_type == search_type).all()
                    print(result_rows)

                    for row in result_rows:
                        html_file.write(f'<li><a href="{row.url}">{row.title}</a></li>')

                    html_file.write('</ul>')

            html_file.write('</html></body>\n')

        print(os.system(html_result_file_name))


