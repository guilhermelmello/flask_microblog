# Microblog with Flask

Microblog app implementation with Flask.

This implementation follows [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world), by Miguel Grinberg.

# How to setup this project

- First download [and unzip] this repository into your machine.
- Enter the microblog directory.
- Create and activate a virtual environment:
```console
foo@bar:~/microblog$ virtualenv venv
foo@bar:~/microblog$ source venv/bin/activate
```

- Install requirements
```console
(venv) foo@bar:~/microblog$ pip install -r requirements.txt
```
- Run flask application
```console
(venv) foo@bar:~/microblog$ flask run
```

- Start a local email server
```console
(venv) foo@bar:~/microblog$ python -m smtpd -n -c DebuggingServer localhost:8025
 ```

