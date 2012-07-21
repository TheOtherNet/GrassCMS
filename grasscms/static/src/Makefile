all:
	coffee --join ./coffee.js --compile coffee/*.coffee
	cat *.js >> grasscms.ajs
	yui-compressor --type js ./grasscms.ajs > grasscms.js
	rm grasscms.ajs
	rm coffee.js
	lessc less/main.less main.css


clean:
	rm grasscms.js


