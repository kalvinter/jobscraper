from Classes.ConfigHandlerClass import ConfigHandler
from Classes.DBHandlerClass import session_scope, Vacancies, Platform
import os
import shutil


class ResultPrinter:

    def __init__(self, dbms):
        self.header = '---- # (ResultPrinter)'
        self.dbms = dbms

    def print_result_to_html(self, seach_topic_list: list, open_html_after_finish: bool = True):
        # Copy the template html-file and use it as new result-html-file
        shutil.copy(src=ConfigHandler.TEMPLATE_HTML_PATH, dst=ConfigHandler.RESULT_HTML_PATH)

        with open(ConfigHandler.RESULT_HTML_PATH, 'a') as html_file:

            result_counter = 0

            with session_scope(dbms=self.dbms) as session:
                # Get all platform names
                platform_names = []
                result_rows = session.query(Platform.name).all()

                for row in result_rows:
                    platform_names.extend(list(row))

                # Print all platform names in the header, hyper-linking to the respective sections
                print(platform_names)
                html_file.write(f'<div class="jump_to_section"><h6>Jump to section ... </h6><ul>\n')

                for search_topic in seach_topic_list:
                    # html_file.write(f'<h6>Search Type: {search_topic}</h6>\n<ul>')

                    for platform in platform_names:
                        html_file.write(f'<li><a href="#{search_topic}_{platform}" class="contents_a">'
                                        f'... Search Topic {search_topic} - {platform}</a></li>')

                    html_file.write(f'</ul></div><div class="header_clear_area"></div>\n')

                for search_topic in seach_topic_list:
                    html_file.write(f'<h5>Search Type: {search_topic}</h5>\n')

                    for platform in platform_names:
                        html_file.write(f'<h6 id="{search_topic}_{platform}">{platform}</h6>')
                        html_file.write('<div class="posting-list-wrapper">')

                        # Get all entries in database for this platform
                        result_rows = session.query(Vacancies)\
                            .filter(Vacancies.platform == platform, Vacancies.search_topic == search_topic).all()
                        print(result_rows)

                        for row in result_rows:
                            result_counter += 1

                            job_item_string = f'<div class="job-item" >' \
                                f'<a class="job-posting" href="{row.url}" target="_blank" ' \
                                f'onclick="activateCheckBox(\'job_checkbox_{result_counter}\', ' \
                                f'\'job_checkbox_label_{result_counter}\', \'outlined\', \'filled\');' \
                                f'event.stopPropagation();">' \
                                f'<div class="job-title-column"><div class="arrow-icon"></div>' \
                                f'<div class="job-title">{row.title}</div>' \
                                f'</div><div class="job-column">' \
                                f'<div class="job-company">{row.company}' \
                                f'</div>' \
                                f'<div class="job-date">{row.date} - {row.location}</div>' \
                                f'</div>' \
                                f'</a>' \
                                f'<div class="job-checkbox">' \
                                f'<label for="job_checkbox_{result_counter}" ' \
                                f'id="job_checkbox_label_{result_counter}" class="checkbox_btn outlined">Checked' \
                                f'<input type="checkbox" style="opacity: 0;"' \
                                f'onclick="toggleCheckBox(\'job_checkbox_{result_counter}\', ' \
                                f'\'job_checkbox_label_{result_counter}\', \'outlined\', \'filled\');' \
                                f'  "' \
                                f'id="job_checkbox_{result_counter}" class="badgebox">' \
                                f'<span class="badge">&nbsp;&check;&nbsp;</span></label>' \
                                f'</div>' \
                                f'</div>'

                            html_file.write(job_item_string)

                        html_file.write('</div><br><br>')

            html_file.write('</body></html>\n')

        if open_html_after_finish:
            os.system(ConfigHandler.RESULT_HTML_FILE_NAME)


