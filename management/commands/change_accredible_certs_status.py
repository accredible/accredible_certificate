from django.core.management.base import BaseCommand, CommandError
from certificates.models import certificate_status_for_student
from accredible_certificate.queue import CertificateGeneration
from django.contrib.auth.models import User
from optparse import make_option
from django.conf import settings
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore
from certificates.models import CertificateStatuses
from certificates.models import GeneratedCertificate
import datetime
from pytz import UTC



class Command(BaseCommand):

    help = """
    Find all students that need certificates for courses that have finished and
    put their cert requests on the accredible API.

    Other commands can be private: true or not?
    Per use need to think about it as when I completed that Edx Linux course now the certificate generated at that time so might be in use
    """

    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    metavar='COURSE_ID',
                    dest='course',
                    default=False,
                    help='Grade and generate certificates '
                    'for a specific course'),    
    )

    def handle(self, *args, **options):

        # Will only generate a certificate if the current
        # status is in the unavailable state, can be set
        # to something else with the force flag


        if options['course']:
            # try to parse out the course from the serialized form
            try:
                course = CourseKey.from_string(options['course'])
            except InvalidKeyError:
                print("Course id {} could not be parsed as a CourseKey; falling back to SSCK.from_dep_str".format(options['course']))
                course = SlashSeparatedCourseKey.from_deprecated_string(options['course'])
            course_id = course
        else:
            raise CommandError("You must specify a course")
        


        for certificate in GeneratedCertificate.objects.filter(course_id=course_id, status="generating"):
            certificate.status = "downloadable"
            certificate.save
            print certificate.name