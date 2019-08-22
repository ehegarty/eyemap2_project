# Notes on deploying the app

## webcourse.cs.nuim.ie

Development deployment: running application within docker container on the webcourse.cs.nuim.ie, via `python manage.py runserver 0.0.0.0:8000`, and configuring Apache2 on that host to redirect ("proxy") requests to eyemap2.cs.nuim.ie to the docker container.

The code itself is copied into `/var/lib/gitlab/eyemap2`, and that directory is bind-mounted to `/app` of the running container. This allows for the database persistence if container ever gets disconnected.

The CI/CD pipeline in the gitlab repository is set up to stop container before new code is copied into `/var/lib/gitlab/eyemap2`, then run database migrations with `python manage.py migrate`, and finally start the container. If container does not exist it will be created with the following invocation: `docker create -v /var/lib/gitlab/eyemap2:/app -p 127.0.0.1:10118:8000 --name eyemap2 eyemap2`

If docker/Dockerfile is modified a new image will be built, but it have not been tested yet if container needs to be deleted in this case.

The following apache2 configuration snippet sets up the proxying:
```
<VirtualHost *:443>
	ServerAdmin support@cs.nuim.ie
	ServerName eyemap2.cs.nuim.ie
    
        ProxyPass "/" "http://127.0.0.1:10118/"
        ProxyPassReverse "/" "http://127.0.0.1:10118/"
        
        CustomLog ${APACHE_LOG_DIR}/eyemap2_access.log combined
        ErrorLog ${APACHE_LOG_DIR}/eyemap2_error.log

        SSLEngine on
        SSLCertificateFile    /etc/apache2/ssl/eyemap2/cert.pem
        SSLCertificateChainFile /etc/apache2/ssl/eyemap2/chain.pem
        SSLCertificateKeyFile /etc/apache2/ssl/eyemap2/privkey.pem
        <Directory />
              Options FollowSymLinks
	      AllowOverride None
        </Directory>
</VirtualHost>
```
