"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment


class Office365button(XBlock):
    button_image = String( default='http://vm1-cloud.iblstudios.com/static/images/officelogo.png', help='IMAGE URL', scope=Scope.content,)
    button_text = String( default='Login', help='Button text', scope=Scope.content,)


    def resource_string(self, path):
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):

        html = self.resource_string("static/html/office365button.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/office365button.css"))
        frag.add_javascript(self.resource_string("static/js/src/office365button.js"))
        frag.initialize_js('office365button')
        return frag

    def studio_view(self, context):
        html_str = self.resource_string("static/html/office365button_edit.html")
        frag = Fragment(unicode(html_str).format(button_text=self.button_text,button_image=self.button_image))

        js_str = self.resource_string("static/js/src/office365button_edit.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('office365buttonEdit')

        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.button_image = data.get('button_image')
        self.button_text = data.get('button_text')

        return {'result': 'success'}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("Office365Button",
             """<vertical_demo>
                <office365button/>
                <office365button/>
                <office365button/>
                </vertical_demo>
             """),
        ]
