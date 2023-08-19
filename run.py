from market import app,cli

# Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
