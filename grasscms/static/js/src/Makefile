all:
	coffee --join ./coffee.js --compile coffee/*.coffee
	cat *.js >> grasscms.ajs
	yui-compressor --type js ./grasscms.ajs > ../grasscms/grasscms.js
	rm grasscms.ajs


