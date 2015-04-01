"""
Reusable mixins for XBlocks and/or XModules
"""

from xblock.fields import Scope, String, XBlockMixin

# Make '_' a no-op so we can scrape strings
_ = lambda text: text


class LicenseMixin(XBlockMixin):
    """
    Mixin that allows an author to indicate a license on the contents of an
    XBlock. For example, a video could be marked as Creative Commons SA-BY
    licensed. You can even indicate the license on an entire course.

    If this mixin is not applied to an XBlock, or if the license field is
    blank, then the content is subject to whatever legal licensing terms that
    apply to content by default. For example, in the United States, that content
    is exclusively owned by the creator of the content by default. Other
    countries may have similar laws.
    """
    license = String(
        display_name=_("License"),
        help=_("A license defines how the contents of this block can be shared and reused."),
        default=None,
        scope=Scope.settings
    )

    @classmethod
    def definition_from_xml(cls, xml_object, system):
        import nose.tools; nose.tools.set_trace()
        license = xml_object.get("license", default=None)
        definition, children = super(LicenseMixin, cls).definition_from_xml(xml_object, system)
        definition['license'] = license
        return definition, children

    def definition_to_xml(self, resource_fs):
        xml_object = super(LicenseMixin, self).definition_to_xml(resource_fs)
        if self.license:
            xml_object.set("license", self.license)
        return xml_object
