import minify_html


class HtmlMinifier:
    def minify(self, html: str) -> str:
        return minify_html.minify(
            html,
            minify_js=False,
            minify_css=False,
            keep_closing_tags=True,
        )
