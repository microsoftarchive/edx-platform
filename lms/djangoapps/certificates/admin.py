"""
django admin pages for certificates models
"""
from django.contrib import admin
from certificates.models import CertificateGenerationConfiguration, CertificateHtmlViewConfiguration


admin.site.register(CertificateGenerationConfiguration)
admin.site.register(CertificateHtmlViewConfiguration)
