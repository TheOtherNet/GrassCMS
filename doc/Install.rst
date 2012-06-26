Under the doc/ directories you've got different configuration for wsgi and 
fcgi, both pointing to a grasscms config file in /var/www/grasscms.com/

Also, if you're not setting debug variable, /var/www/grasscms.com will be 
the default place to look for conf files, wich path will be relative.

Static/ files are usually stored sepparately, and then fixed by 
a redirection. In this case, you should keep a copy of static/ in 
/var/www/grasscms.com/ and make your webserver handle that

Deployment script gives a small example for that.

