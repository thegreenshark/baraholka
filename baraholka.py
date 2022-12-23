from baraholka import app, appSettings

if __name__ == "__main__":
    if appSettings['debugMode']:
        app.run(debug=True,host='localhost', port=5000)
    else:
        app.run(host='0.0.0.0', port=8000)