from certificates.models import GeneratedCertificate
from certificates.models import certificate_status_for_student
from certificates.models import CertificateStatuses as status
from certificates.models import CertificateWhitelist

from courseware import grades, courses
from django.test.client import RequestFactory
from capa.xqueue_interface import XQueueInterface
from capa.xqueue_interface import make_xheader, make_hashkey
from django.conf import settings
from requests.auth import HTTPBasicAuth
from student.models import UserProfile, CourseEnrollment
from verify_student.models import SoftwareSecurePhotoVerification
import json
import random
import logging
import lxml.html
from lxml.etree import XMLSyntaxError, ParserError
import requests
from xmodule.modulestore.django import modulestore




logger = logging.getLogger(__name__)


class CertificateGeneration(object):
    """
    AccredibleCertificate generates an
    accredible certificates for students

    See certificates/models.py for valid state transitions,
    summary of methods:

       add_cert:   Add a new certificate.  Puts a single
                   request on the queue for the student/course.
                   Once the certificate is generated a post
                   will be made to the update_certificate
                   view which will save the certificate
                   download URL.

       regen_cert: Regenerate an existing certificate.
                   For a user that already has a certificate
                   this will delete the existing one and
                   generate a new cert.


       del_cert:   Delete an existing certificate
                   For a user that already has a certificate
                   this will delete his cert.

    """

    def __init__(self, request=None, api_key=None):

        # Get basic auth (username/password) for
        # xqueue connection if it's in the settings


        if request is None:
            factory = RequestFactory()
            self.request = factory.get('/')
        else:
            self.request = request

        self.whitelist = CertificateWhitelist.objects.all()
        self.restricted = UserProfile.objects.filter(allow_certificate=False)
        self.api_key = api_key
        

    def add_cert(self, student, course_id, defined_status="downloadable", course=None, forced_grade=None, template_file=None, title='None'):
        """
        Request a new certificate for a student.

        Arguments:
          student   - User.object
          course_id - courseenrollment.course_id (CourseKey)
          forced_grade - a string indicating a grade parameter to pass with
                         the certificate request. If this is given, grading
                         will be skipped.

        Will change the certificate status to 'generating' or 'downloadable'.

        Certificate must be in the 'unavailable', 'error',
        'deleted' or 'generating' state.

        If a student has a passing grade or is in the whitelist
        table for the course a request will be made for a new cert.

        If a student has allow_certificate set to False in the
        userprofile table the status will change to 'restricted'

        If a student does not have a passing grade the status
        will change to status.notpassing

        Returns the student's status
        """

        VALID_STATUSES = [status.generating,
                          status.unavailable,
                          status.deleted,
                          status.error,
                          status.notpassing]

        cert_status = certificate_status_for_student(student, course_id)['status']

        new_status = cert_status

        if cert_status in VALID_STATUSES:
            # grade the student

            # re-use the course passed in optionally so we don't have to re-fetch everything
            # for every student
            if course is None:
                course = courses.get_course_by_id(course_id)
            profile = UserProfile.objects.get(user=student)
            profile_name = profile.name

            # Needed
            self.request.user = student
            self.request.session = {}

            course_name = course.display_name or course_id.to_deprecated_string()
            description = ''
            for section_key in ['short_description', 'description','overview']:
                loc = loc = course.location.replace(category='about', name=section_key)
                try:
                    if modulestore().get_item(loc).data:
                       description = modulestore().get_item(loc).data
                       break
                except:
                    print "this course don't have " +section_key
              
            if not description:
               description = "course_description"


            is_whitelisted = self.whitelist.filter(user=student, course_id=course_id, whitelist=True).exists()
            grade = grades.grade(student, self.request, course)
            enrollment_mode, __ = CourseEnrollment.enrollment_mode_for_user(student, course_id)
            mode_is_verified = (enrollment_mode == GeneratedCertificate.MODES.verified)
            user_is_verified = SoftwareSecurePhotoVerification.user_is_verified(student)
            user_is_reverified = SoftwareSecurePhotoVerification.user_is_reverified_for_all(course_id, student)
            cert_mode = enrollment_mode
            if (mode_is_verified and not (user_is_verified and user_is_reverified)):
                cert_mode = GeneratedCertificate.MODES.honor
            
            if forced_grade:
                grade['grade'] = forced_grade

            cert, __ = GeneratedCertificate.objects.get_or_create(user=student, course_id=course_id)

            cert.mode = cert_mode
            cert.user = student
            cert.grade = grade['percent']
            cert.course_id = course_id
            cert.name = profile_name
            # Strip HTML from grade range label
            grade_contents = grade.get('grade', None)
            try:
                grade_contents = lxml.html.fromstring(grade_contents).text_content()
            except (TypeError, XMLSyntaxError, ParserError) as e:
                #   Despite blowing up the xml parser, bad values here are fine
                grade_contents = None

            if is_whitelisted or grade_contents is not None:

                # check to see whether the student is on the
                # the embargoed country restricted list
                # otherwise, put a new certificate request
                # on the queue
                print grade_contents
                if self.restricted.filter(user=student).exists():
                    new_status = status.restricted
                    cert.status = new_status
                    cert.save()
                else:
                    contents = {
                        'action': 'create',
                        'username': student.username,
                        'course_id': course_id.to_deprecated_string(),
                        'course_name': course_name,
                        'name': profile_name,
                        'grade': grade_contents
                    }
                    if defined_status == "generating":
                      approve = False
                    else:
                      approve = True

                    grade_into_string =  ''.join('{}{}'.format(key, val) for key, val in grade.items())
                    payload = {"credential": { "name": course_name, "description": description, "achievement_id": contents['course_id'] , "course_link": "/courses/" +contents['course_id'] + "/about", "approve": approve, "template_name": contents['course_id'] ,"grade": grade_contents, "recipient": {"name": contents['name'], "email": student.email},"evidence_items": [{"description": "Course Transcript", "category": "transcript", "string_object": json.dumps(grade["section_breakdown"])}, {"description": "Final Grade", "category": "grade", "string_object": grade['percent']}]}}
                    payload = json.dumps(payload)
                    r = requests.post('https://api.accredible.com/v1/credentials', payload, headers={'Authorization':'Token token=' + self.api_key, 'Content-Type':'application/json'})
                    
                    if r.status_code == 200:
                       json_response = r.json()  
                       cert.status = defined_status
                       cert.key = json_response["credential"]["id"]
                       if 'private' in json_response:
                          cert.download_url = "https://wwww.accredible.com/" + str(json_response["credential"]["id"]) + "?key" + str(json_response["private_key"])
                       else:
                          cert.download_url = "https://www.accredible.com/" + str(cert.key)
                       cert.save()
                    else:
                        new_status = "errors"
                    

            else:
                cert_status = status.notpassing
                cert.status = cert_status
                cert.save()

        return new_status



