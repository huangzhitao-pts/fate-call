from server import create_app


if __name__ == "__main__":
    app = create_app("deployment")
    app.run(host="192.168.89.155", debug=True)