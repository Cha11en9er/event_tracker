from website import create_app, socketio_app

app, socketio_app = create_app()

if __name__ == '__main__':
    # app.run(debug = True)
    socketio_app.run(app, debug=True)