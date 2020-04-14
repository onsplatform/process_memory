debug: export FLASK_ENV=development
debug:
	@flask run --port 8009
run:
	@gunicorn wsgi:process_memory_app --bind 0.0.0.0:8009 --log-level debug --log-file - --timeout 30000
