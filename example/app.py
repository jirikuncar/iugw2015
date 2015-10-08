from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    # We run in debug mode on port 5000.
    app.run(host="0.0.0.0", port=5000, debug=True)
