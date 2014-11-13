Installing the repo: 
 1) sudo git submodule add https://github.com/deependersingla/accredible_certificate   /edx/app/edxapp/edx-platform/lms/djangoapps/accredible_certificate.
 Benefit git submodule is that it add it can help in update very easily.

 2) Edit lms/envs/common.py around line 1326 you will see installed apps, include accredible_certificate also there.
 
 3) Visit https://accredible.com/issuer/sign_up and get one API KEY, its free :)
 
 Assuming you are on the server and changed to the /edx/app/edxapp/edx-platform directory to use manage.py
 Run shell commands to see if installation is proper: sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings=aws help
 
 You will see:
[accredible_certificates]
    change_accredible_certs_status
    generate_accredible_certs

also in the available commands.

IF you see this then everything is fine and you are ready to generate certificate.
Also for Rolling certificate: 
1)  Add API key to views file in the directory around line: 31
2) Update lms/urls.py change this line: url(r'^request_certificate$', 'certificates.views.request_certificate'), with the new_line url(r'^request_certificate$', 'accredible_certificate.views.request_certificate')


Using the Repo: Login to the server and change to the /edx/app/edxapp/edx-platform directory to use manage.py

1) Change in default styling of certifcate for a particular course:
   a) Command: sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings aws generate_accredible_certs -c   edX/DemoX/Demo_Course -a <API_KEY> -s True
   
   b) After this go to your Managemenrt console and desgin certificate. Click on publish. All the course students are notified        for their certificate.

   c) In the console command: sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings aws    change_accredible_certs_status -c edX/DemoX/Demo_Course This command changes status of generating certificate from generating to       download. Now student can see the Accredible certificate in lms also.

2) No change in default styling from Provider level style preferences:
   a) Just run this command: sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings aws generate_accredible_certs -c edX/DemoX/Demo_Course -a <API_KEY>
   
For rolling Certificate no change it will work the way, they are working now, after installation. If you want to update any of the certificate visit management console or use Accredible API.

For any doubt please send a email to deepender281190@gmail.com or support@accredible.com. You will get reply in no time.


