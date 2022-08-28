# Yatube web service

<p align="right">
<a href="https://docs.python.org/3.7/">
<img src="https://img.shields.io/badge/Python-3.7-FFE873.svg?labelColor=4B8BBE" 
alt="Python requirement: 3.7">
</a>
</p>

## About

A web service for social network of bloggers. The service allows you view 
posts of other users or create/edit your posts on the site. In the latter case 
you need to create your account on the site and to log in.

On the service, you can view all posts, posts written by a specific author 
or posts belonging to a specific group. When you create/edit a post, you 
can select a group from a dedicated list to which your post will belong. 

In addition to creating/editing posts, authorized users can follow the authors 
they like and separately see their 
latest posts. Authorized users can also leave comments on all posts.

You can check out the service here:
[https://yo1k.pythonanywhere.com/](https://yo1k.pythonanywhere.com/)

Tech stack: \
[Django 2.2](https://docs.djangoproject.com/en/2.2/), 
[Bootstrap 5.0](https://getbootstrap.com/)

## Running the project in developer mode

* Clone this repo.
* Install [Python 3.7](https://docs.python.org/3.7/).
* Follow these manual steps using this [guide](https://docs.python.org/3.7/tutorial/venv.html):
  * Create Python virtual environment for your project.
  * Activate project's virtual environment.
  * Install all project dependencies in the project's virtual environment 
    using `requirements.txt`:
```shell
$ pip install -r requirements.txt
```
* Change the current working directory to `./yatube` where `manage.py` is 
  located and run the command:
```shell
$ python3 manage.py runserver
```
