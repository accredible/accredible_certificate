sudo git submodule add https://github.com/deependersingla/accredible_certificate /edx/app/edxapp/edx-platform/lms/djangoapps/accredible_certificates

Other benefit of using git submodule is that it add it can help in update easily by running git submodule update.

Edit lms/envs/common.py around line 1326 you will see installed apps, include accredible_certificate also there.

Now afer adding the repo run shell commands to see if the accredible command generate_accredible_certs is avialable: Run
sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings=aws help

You will see:
[accredible_certificates]
    change_accredible_certs_status
    generate_accredible_certs

also in the available commands.

sudo -u www-data /edx/bin/python.edxapp ./manage.py lms --settings aws generate_accredible_certs -c edX/DemoX/Demo_Course -a "accredible_secret123" -s True

Also for Rolling certificate
