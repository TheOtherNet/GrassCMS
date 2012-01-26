We've only tried WSGI deploy right now, but this could be done just as any other FLASK app, except for configuring the output folder for the uploaded files.
I extrongly recommend doing so by editing the .wsgi file (currently pointing to /var/www/grasscms/uploads), remember to give uploads your webserver's permisions.
