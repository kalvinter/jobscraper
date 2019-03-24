from Classes.ConfigHandlerClass import ConfigHandler
from Classes.DBHandlerClass import session_scope, Vacancies, Platform
import os


class ResultPrinter:

    def __init__(self, dbms, browser):
        self.header = '---- # (ResultPrinter)'
        self.dbms = dbms
        self.browser = browser
        self.vacancy_template = "<li>{}</li>"

        self.html_file_header = f'<html><head><style>'\
            'a {color: rgb(0, 0, 238);}      /* unvisited link */'\
            'a:visited {color: rgb(0, 0, 238);}  /* visited link */'\
            'a:hover {color: rgba(117, 117, 255, 1);}  /* mouse over link */'\
            'a:active {color: #0000FF;}  /* selected link */ '\
            '</style></head>\n'

    def print_result_to_html(self, seach_topic_list: list, open_html_after_finish: bool = True):
        with open(ConfigHandler.RESULT_HTML_PATH, 'w') as html_file:
            html_file.write(self.html_file_header)

            for search_topic in seach_topic_list:
                html_file.write(f'<body><h1>Search Type: {search_topic}</h1>\n')

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
                            .filter(Vacancies.platform == platform, Vacancies.search_topic == search_topic).all()
                        print(result_rows)

                        for row in result_rows:
                            html_file.write(f'<li style="padding-bottom: 4px;"><a style="text-decoration: none;" '
                                            f'href="{row.url}">{row.title}</a> ({row.company})</li>')

                        html_file.write('</ul><br>')

            html_file.write('</html></body>\n')

        if open_html_after_finish:
            os.system(ConfigHandler.RESULT_HTML_FILE_NAME)


