PREFIX=debian/python3-cyberfusion-rabbitmq-consumer-log-server/

install:
	mkdir -p $(PREFIX)usr/share/rabbitmq-consumer-log-server/

	cp alembic.debian.ini $(PREFIX)usr/share/rabbitmq-consumer-log-server/alembic.ini

	rsync -a migrations/ $(PREFIX)usr/share/rabbitmq-consumer-log-server/migrations/
	rsync -a templates/ $(PREFIX)usr/share/rabbitmq-consumer-log-server/templates/
	rsync -a static/ $(PREFIX)usr/share/rabbitmq-consumer-log-server/static/


uninstall:
	rm -r $(PREFIX)usr/share/rabbitmq-consumer-log-server/

clean:
	echo "NOP"
