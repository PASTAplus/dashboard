# Dashboard
PASTA system dashboard and utilities

The PASTA Dashboard is a Flask driven web application using Ngnix as its frontend
web server. Some routes require administration rights to access, but most routes
are publicly accessible.

## Deployment notes
- To install `uwsgi` with Conda: `conda install -c conda-forge uwsgi`
- To restart service: `sudo service dashboard restart`
- Flask requires all static content to be in `<webapp>/static`
  (see Config.STATIC)

Thanks to Digital Oceans' community tutorials for tips on deploying [Nginx with LetsEncrypt on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04) and integrating [Flask and uwsgi with Nginx](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04).