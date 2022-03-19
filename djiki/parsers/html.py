from lxml.html.clean import Cleaner


class SafeHTML(object):
    def __init__(self):
        self.cleaner = Cleaner(
            scripts=True,
            javascript=True,
            style=True,
            page_structure=True,
            annoying_tags=True,
            remove_unknown_tags=True,
        )

    def render(self, src):
        return self.cleaner.clean_html(src)
