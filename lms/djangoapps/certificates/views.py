"""URL handlers related to certificate handling by LMS"""
from datetime import datetime
import dogstats_wrapper as dog_stats_api
import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from capa.xqueue_interface import XQUEUE_METRIC_NAME
from certificates.models import (
    certificate_status_for_student,
    CertificateStatuses,
    GeneratedCertificate,
    ExampleCertificate,
    CertificateHtmlViewConfiguration
)
from certificates.queue import XQueueCertInterface
from edxmako.shortcuts import render_to_response
from xmodule.modulestore.django import modulestore
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from util.json_request import JsonResponse, JsonResponseBadRequest
from util.bad_request_rate_limiter import BadRequestRateLimiter

logger = logging.getLogger(__name__)


@csrf_exempt
def request_certificate(request):
    """Request the on-demand creation of a certificate for some user, course.

    A request doesn't imply a guarantee that such a creation will take place.
    We intentionally use the same machinery as is used for doing certification
    at the end of a course run, so that we can be sure users get graded and
    then if and only if they pass, do they get a certificate issued.
    """
    if request.method == "POST":
        if request.user.is_authenticated():
            xqci = XQueueCertInterface()
            username = request.user.username
            student = User.objects.get(username=username)
            course_key = SlashSeparatedCourseKey.from_deprecated_string(request.POST.get('course_id'))
            course = modulestore().get_course(course_key, depth=2)

            status = certificate_status_for_student(student, course_key)['status']
            if status in [CertificateStatuses.unavailable, CertificateStatuses.notpassing, CertificateStatuses.error]:
                log_msg = u'Grading and certification requested for user %s in course %s via /request_certificate call'
                logger.info(log_msg, username, course_key)
                status = xqci.add_cert(student, course_key, course=course)
            return HttpResponse(json.dumps({'add_status': status}), mimetype='application/json')
        return HttpResponse(json.dumps({'add_status': 'ERRORANONYMOUSUSER'}), mimetype='application/json')


@csrf_exempt
def update_certificate(request):
    """
    Will update GeneratedCertificate for a new certificate or
    modify an existing certificate entry.

    See models.py for a state diagram of certificate states

    This view should only ever be accessed by the xqueue server
    """

    status = CertificateStatuses
    if request.method == "POST":

        xqueue_body = json.loads(request.POST.get('xqueue_body'))
        xqueue_header = json.loads(request.POST.get('xqueue_header'))

        try:
            course_key = SlashSeparatedCourseKey.from_deprecated_string(xqueue_body['course_id'])

            cert = GeneratedCertificate.objects.get(
                user__username=xqueue_body['username'],
                course_id=course_key,
                key=xqueue_header['lms_key'])

        except GeneratedCertificate.DoesNotExist:
            logger.critical('Unable to lookup certificate\n'
                            'xqueue_body: {0}\n'
                            'xqueue_header: {1}'.format(
                                xqueue_body, xqueue_header))

            return HttpResponse(json.dumps({
                'return_code': 1,
                'content': 'unable to lookup key'}),
                mimetype='application/json')

        if 'error' in xqueue_body:
            cert.status = status.error
            if 'error_reason' in xqueue_body:

                # Hopefully we will record a meaningful error
                # here if something bad happened during the
                # certificate generation process
                #
                # example:
                #  (aamorm BerkeleyX/CS169.1x/2012_Fall)
                #  <class 'simples3.bucket.S3Error'>:
                #  HTTP error (reason=error(32, 'Broken pipe'), filename=None) :
                #  certificate_agent.py:175

                cert.error_reason = xqueue_body['error_reason']
        else:
            if cert.status in [status.generating, status.regenerating]:
                cert.download_uuid = xqueue_body['download_uuid']
                cert.verify_uuid = xqueue_body['verify_uuid']
                cert.download_url = xqueue_body['url']
                cert.status = status.downloadable
            elif cert.status in [status.deleting]:
                cert.status = status.deleted
            else:
                logger.critical('Invalid state for cert update: {0}'.format(
                    cert.status))
                return HttpResponse(
                    json.dumps({
                        'return_code': 1,
                        'content': 'invalid cert status'
                    }),
                    mimetype='application/json'
                )

        dog_stats_api.increment(XQUEUE_METRIC_NAME, tags=[
            u'action:update_certificate',
            u'course_id:{}'.format(cert.course_id)
        ])

        cert.save()
        return HttpResponse(json.dumps({'return_code': 0}),
                            mimetype='application/json')


@csrf_exempt
@require_POST
def update_example_certificate(request):
    """Callback from the XQueue that updates example certificates.

    Example certificates are used to verify that certificate
    generation is configured correctly for a course.

    Unlike other certificates, example certificates
    are not associated with a particular user or displayed
    to students.

    For this reason, we need a different end-point to update
    the status of generated example certificates.

    Arguments:
        request (HttpRequest)

    Returns:
        HttpResponse (200): Status was updated successfully.
        HttpResponse (400): Invalid parameters.
        HttpResponse (403): Rate limit exceeded for bad requests.
        HttpResponse (404): Invalid certificate identifier or access key.

    """
    logger.info(u"Received response for example certificate from XQueue.")

    rate_limiter = BadRequestRateLimiter()

    # Check the parameters and rate limits
    # If these are invalid, return an error response.
    if rate_limiter.is_rate_limit_exceeded(request):
        logger.info(u"Bad request rate limit exceeded for update example certificate end-point.")
        return HttpResponseForbidden("Rate limit exceeded")

    if 'xqueue_body' not in request.POST:
        logger.info(u"Missing parameter 'xqueue_body' for update example certificate end-point")
        rate_limiter.tick_bad_request_counter(request)
        return JsonResponseBadRequest("Parameter 'xqueue_body' is required.")

    if 'xqueue_header' not in request.POST:
        logger.info(u"Missing parameter 'xqueue_header' for update example certificate end-point")
        rate_limiter.tick_bad_request_counter(request)
        return JsonResponseBadRequest("Parameter 'xqueue_header' is required.")

    try:
        xqueue_body = json.loads(request.POST['xqueue_body'])
        xqueue_header = json.loads(request.POST['xqueue_header'])
    except (ValueError, TypeError):
        logger.info(u"Could not decode params to example certificate end-point as JSON.")
        rate_limiter.tick_bad_request_counter(request)
        return JsonResponseBadRequest("Parameters must be JSON-serialized.")

    # Attempt to retrieve the example certificate record
    # so we can update the status.
    try:
        uuid = xqueue_body.get('username')
        access_key = xqueue_header.get('lms_key')
        cert = ExampleCertificate.objects.get(uuid=uuid, access_key=access_key)
    except ExampleCertificate.DoesNotExist:
        # If we are unable to retrieve the record, it means the uuid or access key
        # were not valid.  This most likely means that the request is NOT coming
        # from the XQueue.  Return a 404 and increase the bad request counter
        # to protect against a DDOS attack.
        logger.info(u"Could not find example certificate with uuid '%s' and access key '%s'", uuid, access_key)
        rate_limiter.tick_bad_request_counter(request)
        raise Http404

    if 'error' in xqueue_body:
        # If an error occurs, save the error message so we can fix the issue.
        error_reason = xqueue_body.get('error_reason')
        cert.update_status(ExampleCertificate.STATUS_ERROR, error_reason=error_reason)
        logger.warning(
            (
                u"Error occurred during example certificate generation for uuid '%s'.  "
                u"The error response was '%s'."
            ), uuid, error_reason
        )
    else:
        # If the certificate generated successfully, save the download URL
        # so we can display the example certificate.
        download_url = xqueue_body.get('url')
        if download_url is None:
            rate_limiter.tick_bad_request_counter(request)
            logger.warning(u"No download URL provided for example certificate with uuid '%s'.", uuid)
            return JsonResponseBadRequest(
                "Parameter 'download_url' is required for successfully generated certificates."
            )
        else:
            cert.update_status(ExampleCertificate.STATUS_SUCCESS, download_url=download_url)
            logger.info("Successfully updated example certificate with uuid '%s'.", uuid)

    # Let the XQueue know that we handled the response
    return JsonResponse({'return_code': 0})


# pylint: disable=too-many-statements, bad-continuation
@login_required
def render_html_view(request):
    """
    This view generates an HTML representation of the specified student's certificate
    If a certificate is not available, we display a "Sorry!" screen instead
    """
    invalid_template_path = 'certificates/invalid.html'

    # Feature Flag check
    if not settings.FEATURES.get('CERTIFICATES_HTML_VIEW', False):
        return render_to_response(invalid_template_path)

    context = {}
    course_id = request.GET.get('course', None)
    context['course'] = course_id
    if not course_id:
        return render_to_response(invalid_template_path, context)

    # Course Lookup
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        return render_to_response(invalid_template_path, context)
    course = modulestore().get_course(course_key)
    if not course:
        return render_to_response(invalid_template_path, context)

    # Certificate Lookup
    try:
        certificate = GeneratedCertificate.objects.get(
            user=request.user,
            course_id=course_key
        )
    except GeneratedCertificate.DoesNotExist:
        return render_to_response(invalid_template_path, context)

    # Load static output values from configuration,
    configuration = CertificateHtmlViewConfiguration.get_config()
    context = configuration.get('default', {})
    # Override the defaults with any mode-specific static values
    context.update(configuration.get(certificate.mode, {}))
    # Override further with any course-specific static values
    context.update(course.cert_html_view_overrides)

    # Populate dynamic output values using the course/certificate data loaded above
    user_fullname = request.user.profile.name
    company_name = context.get('company_name')
    context['accomplishment_copy_name'] = user_fullname
    context['accomplishment_copy_course_org'] = course.org
    context['accomplishment_copy_course_name'] = course.display_name
    context['certificate_id_number'] = certificate.verify_uuid
    context['certificate_verify_url'] = _("{prefix}{uuid}{suffix}").format(
        prefix=context.get('certificate_verify_url_prefix'),
        uuid=certificate.verify_uuid,
        suffix=context.get('certificate_verify_url_suffix')
    )
    context['logo_alt'] = company_name

    accd_course_org_html = '<span class="detail--xuniversity">{org}</span>'.format(org=course.org)
    accd_company_name_html = '<span class="detail--company">{company_name}</span>'.format(company_name=company_name)
    # Translators:
    context['accomplishment_copy_course_description'] = _('a course of study offered by {org}, through {name}.').format(
        org=accd_course_org_html,
        name=accd_company_name_html
    )

    # Translators:
    context['accomplishment_more_title'] = _("More Information About {user_name}'s Certificate:").format(
        user_name=user_fullname
    )

    # Translators:
    context['certificate_date_issued_title'] = _("Issued On:")

    # Translators:
    context['certificate_date_issued'] = _('{month} {day}, {year}').format(
        month=certificate.modified_date.strftime("%B"),
        day=certificate.modified_date.day,
        year=certificate.modified_date.year
    )

    # Translators:
    context['certificate_id_number_title'] = _('Certificate ID Number')

    # Translators:
    context['certificate_info_title'] = _('About {company_name} Certificates').format(
        company_name=company_name
    )

    cert_info_honor_code_html = "<a href='{tos_url}'>{company_name} Honor Code</a>".format(
        tos_url=context.get('company_tos_url'),
        company_name=company_name
    )
    cert_info_verified_html = "<a href='{verified_cert_url}'>verifying your identity</a>".format(
        verified_cert_url=context.get('company_verified_certificate_url')
    )
    # Translators:
    context['certificate_info_description'] = _("{company_name} acknowledges achievements through certificates, which "
                                                "are awarded for various activities {company_name} students complete "
                                                "under the {honor_code_html}.  Some certificates require completing "
                                                "additional steps, such as {verifying_html}.").format(
        company_name=company_name,
        honor_code_html=cert_info_honor_code_html,
        verifying_html=cert_info_verified_html
    )

    # Translators:
    context['certificate_type_title'] = _('{certificate_type} Certfificate').format(
        certificate_type=context.get('certificate_type')
    )

    # Translators:
    context['certificate_verify_title'] = _("How {company_name} Validates Student Certificates").format(
        company_name=company_name
    )

    # Translators:
    context['certificate_verify_description'] = _("Certificates issued by {company_name} are signed by a gpg key so "
                                                  "that they can be validated independently by anyone with the "
                                                  "{company_name} public key. For independent verification, "
                                                  "{company_name} uses what is called a "
                                                  "&quot;detached signature&quot;.").format(company_name=company_name)

    # Translators:
    context['certificate_verify_urltext'] = _("Validate this certificate for yourself")

    # Translators:
    context['company_about_description'] = _("{company_name} offers interactive online classes and MOOCs from the "
                                             "world's best universities, including MIT, Harvard, Berkeley, University "
                                             "of Texas, and many others.  {company_name} is a non-profit online "
                                             "initiative created by founding partners Harvard and MIT.").format(
        company_name=company_name
    )

    # Translators:
    context['company_about_title'] = _("About {company_name}").format(company_name=company_name)

    # Translators:
    context['company_about_urltext'] = _("Learn more about {company_name}").format(company_name=company_name)

    # Translators:
    context['company_courselist_urltext'] = _("Learn with {company_name}").format(company_name=company_name)

    # Translators:
    context['company_careers_urltext'] = _("Work at {company_name}").format(company_name=company_name)

    # Translators:
    context['company_contact_urltext'] = _("Contact {company_name}").format(company_name=company_name)

    # Translators:
    context['company_privacy_urltext'] = _("Privacy Policy")

    # Translators:
    context['company_tos_urltext'] = _("Terms of Service &amp; Honor Code")

    # Translators:
    context['document_banner'] = _("{company_name} acknowledges the following student accomplishment").format(
        company_name=company_name
    )

    # Translators:
    context['logo_subtitle'] = _("Certificate Validation")

    if certificate.mode == 'honor':
        # Translators:
        context['certificate_type_description'] = _("An {cert_type} Certificate signifies that an {company_name} "
                                                    "learner has agreed to abide by {company_name}'s honor code and "
                                                    "completed all of the required tasks for this course under its "
                                                    "guidelines.").format(
            cert_type=context.get('certificate_type'),
            company_name=company_name
        )
    elif certificate.mode == 'verified':
        # Translators:
        context['certificate_type_description'] = _("An {cert_type} Certificate signifies that an {company_name} "
                                                    "learner has agreed to abide by {company_name}'s honor code and "
                                                    "completed all of the required tasks for this course under its "
                                                    "guidelines, as well as having their photo ID checked to verify "
                                                    "their identity.").format(
            cert_type=context.get('certificate_type'),
            company_name=company_name
        )
    elif certificate.mode == 'xseries':
        # Translators:
        context['certificate_type_description'] = _("An {cert_type} Certificate demonstrates a high level of "
                                                    "achievement in a program of study, and includes verification of "
                                                    "the student's identity.").format(
            cert_type=context.get('certificate_type')
        )

    # Translators:
    context['copyright_text'] = _('&copy; {year} {company_name}. All rights reserved.').format(
        year=datetime.now().year,
        company_name=company_name
    )

    # Translators:
    context['document_meta_description'] = _('This is a valid {company_name} certificate for {user_name}, '
                                             'who participated in {course_org} {course_number}').format(
        company_name=company_name,
        user_name=user_fullname,
        course_org=course.org,
        course_number=course.number
    )

    # Translators:
    context['document_title'] = _("Valid {course_org} {course_number} Certificate | {company_name}").format(
        course_org=course.org,
        course_number=course.number,
        company_name=company_name
    )

    # Translators:
    context['accomplishment_copy_description_full'] = _("successfully completed, received a passing grade, and was "
                                                        "awarded a {company_name} {certificate_type} "
                                                        "Certificate of Completion in ").format(
        company_name=company_name,
        certificate_type=context.get("certificate_type")
    )

    return render_to_response("certificates/valid.html", context)
