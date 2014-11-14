
### Pre-installation
Before installing the module please visit https://accredible.com and obtain a free API key.

### Installation
To install the git submodule onto your OpenEdx instance please ensure you have your API key and then follow these steps:

 1. Locate your OpenEdx platform and navigate to **edx-platform**.
 2. Run `sudo git submodule add https://github.com/accredible/accredible_certificate   /edx/app/edxapp/edx-platform/lms/djangoapps/accredible_certificate`
 3. Still within **edx-platform**, edit lms/envs/common.py. Around line 1326 you will the *INSTALLED_APPS* section, include accredible_certificate there by adding the line: `'accredible_certificate',` and saving the updated file.

Now we can check the installation by running shell commands to see if our additional functions are available. Within the **edx-plaform** directory run `sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings=aws help`
 
 Within the long list you should see the following output:

>  [accredible_certificates]
> 	    change_accredible_certs_status
> 	    generate_accredible_certs

If you'd like to generate certificates for **self-paced courses** then we need to make a few further amendments.

 1. From the **edx-platform** directory, edit lms/djangoapps/accredible_certificate/views.py
 2. Find `Your_API_KEY` and replace this with the API key provided via Accredible (it's around line 31). Save this updated file.
 3. From the **edx-platform** directory, edit lms/urls.py 
 4. Find the line: `url(r'^request_certificate$', 'certificates.views.request_certificate'),` and replace this line with: `url(r'^request_certificate$', 'accredible_certificate.views.request_certificate'),` and save this updated file.

### Issuing Certificates
Your account has a default template for how your certificates will appear which you can edit from your dashboard.

If you'd like to issue certificates and update their appearance *before* they are published (sent to your students) then please follow the instructions in **Method A**. If you'd like to issue certificates and have them delivered directly to students without amending their appearance then please follow the instructions in **Method B**.

####Method A
To issue certificates and update their appearance *before* they are published (sent to your students):

 1. Login to your server and navigate to your **edx-platform** directory to use manage.py
 2. Run the command: `sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings aws generate_accredible_certs -c   edX/DemoX/Demo_Course -a <API_KEY> -s True` where < API_KEY > is replaced with the API key provided by Accredible and where edX/DemoX/Demo_Course is replaced by your course key.
 3. Go to the Accredible management console and in your account amend the certificate design to meet your requirements.
 4. In the Accredible management console publish the certificates and they will be delivered to your students.
 5. Back in your console within the **edx-platform** directory, run the command: `sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings aws    change_accredible_certs_status -c edX/DemoX/Demo_Course`. This command pull data from the Accredible API to change the status of the certificates from *generating* to *available for download*. Your students can now view their certificates through the LMS and via their email.


#####Method B
To issue certificates and have them delivered directly to students without amending their appearance:

 1. From the **edx-platform** directory run the command `sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings aws generate_accredible_certs -c edX/DemoX/Demo_Course -a <API_KEY>` where < API_KEY > is replaced with the API key provided by Accredible and where edX/DemoX/Demo_Course is replaced by your course key.

### Support
If you have any issues, suggestions or questions then please send an email to support@accredible.com.


