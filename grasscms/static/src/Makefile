# Makefile for grasscms persistence plugin

all: build compress

compress:
	yui-compressor --type js ./grasscms.js > grasscms.min.js
	yui-compressor --type css grasscms.css > grasscms.min.css

build:
	coffee --join ./grasscms.js --compile coffee/*.coffee
	lessc less/main.less grasscms.css

clean:
	rm grasscms.js grasscms.min.js grasscms.css grasscms.min.css

.PONY: clean build compress all
