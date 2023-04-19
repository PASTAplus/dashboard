# Dashboard
PASTA system dashboard and utilities

The PASTA Dashboard is a Flask driven web application using Ngnix as its frontend
web server. Some routes require administration rights to access, but most routes
are publicly accessible.

## Deployment notes
- To install `uwsgi` with Conda: `conda install -c conda-forge libiconv uwsgi`
- To restart service: `sudo service dashboard restart`
- Flask requires all static content to be in `<webapp>/static`
  (see Config.STATIC)

Thanks to Digital Oceans' community tutorials for tips on deploying [Nginx with LetsEncrypt on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04) and integrating [Flask and uwsgi with Nginx](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04).

## Full deployment steps:
1. Install Nginx - see above
1. Install LetsEncrypt - see above
1. Install git
1. Create the main user - generally _**pasta**_
1. Download and install [_**miniconda**_](https://docs.conda.io/en/latest/miniconda.html)
1. Using the _**conda**_ package manager, create three new Python virtual environments:
  * `conda env create -n pastaplus_utilities python=3.7 --no-default-packages`
  * `conda env create -n soh python=3.7 --no-default-packages`
  * `conda env create -n dashboard python=3.7 --no-default-packages`
1. In the _**pasta**_ home directory, clone the following git repositories:
  * `git clone https://github.com/PASTAplus/pastaplus_utilities.git`
  * `git clone https://github.com/PASTAplus/soh.git`
  * `git clone https://github.com/PASTAplus/dashboard.git`
