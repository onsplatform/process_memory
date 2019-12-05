"""
 Process Memory Web Server Gateway Interface (WSGI) entry point.
 From root, run with:
 gunicorn wsgi:process_memory_app
"""
import process_memory

process_memory_app = process_memory.create_app()

if __name__ == "__main__":
    process_memory_app.run()
