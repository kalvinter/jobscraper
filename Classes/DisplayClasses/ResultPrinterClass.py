from Classes.UtilClasses.ConfigHandlerClass import ConfigHandler
from Classes.UtilClasses.DBHandlerClass import session_scope, Vacancies, Platform
import os
import shutil


class ResultPrinter:

    def __init__(self, dbms, platform_registry, verbose: bool = False):
        self.header = '---- # (ResultPrinter)'
        self.dbms = dbms
        self.platform_registry = platform_registry
        self.verbose = ConfigHandler.VERBOSE_SETTING

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
                if self.verbose:
                    print(f"{self.header}: Printing entries for platforms {str(platform_names)}")

                html_file.write(f'<div class="jump_to_section"><h6>Jump to section ... </h6><ul>\n')

                for search_topic in seach_topic_list:
                    # html_file.write(f'<h6>Search Type: {search_topic}</h6>\n<ul>')

                    for platform in platform_names:
                        html_file.write(f'<li><a href="#{search_topic}_{platform}" class="contents_a">'
                                        f'... Search-Topic {search_topic} - {platform}</a></li>')

                    html_file.write(f'</ul></div><div class="header_clear_area"></div>\n')

                # Print main body with all entries
                for search_topic in seach_topic_list:
                    html_file.write(f"<h5>Search-Topic '{search_topic}'</h5>\n")

                    for platform in platform_names:
                        platform_instance = self.platform_registry.get_platform_instance(platform)

                        if search_topic not in platform_instance.scrape_status:
                            # Each platform could have its own search topic. Only proceed if this search topic
                            # was applied to this platform_instance
                            continue

                        html_file.write(f'<h6 id="{search_topic}_{platform}">{platform} - Job postings</h6>')
                        html_file.write('<div class="posting-list-wrapper">')

                        if not platform_instance.scrape_status[search_topic]:
                            # If a negative scrape status -> print error-message and jump to next platform
                            html_file.write('<p class="error_message message">An error occurred when trying to '
                                            'scrape entries from the platform {platform}</p><br></div>')
                            continue

                        # Get all entries in database for this platform
                        result_rows = session.query(Vacancies)\
                            .filter(Vacancies.platform == platform, Vacancies.search_topic == search_topic).all()

                        if self.verbose:
                            print(result_rows)

                        if len(result_rows) == 0:
                            html_file.write('<p class="message">No job postings found</p>')

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


