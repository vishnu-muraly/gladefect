from scripts import app

if __name__ == '__main__':
    # decide what port to run the app in
    port = int(os.environ.get('PORT', 8000))
    # run the app locally on the givn port
    app.run(host='0.0.0.0', port=port)
    # optional if we want to run in debugging mode
    app.run(debug=True)
