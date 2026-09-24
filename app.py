from flask import Flask, render_template, request, redirect, url_for, make_response, abort, session
import secrets


app = Flask(__name__)
app.secret_key = "super-secret-key-change-me"


@app.route("/")
def red():
    return redirect('/login')


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/hack")
def hack():
    return render_template("attack.html")


@app.route("/dashboard")
def dashboard():
    token = generate_csrf_token()
    if request.cookies.get("role") == "guest":
        return render_template("dashboard.html", csrf_token=token)
    else:
        abort(403)


@app.route("/guest")
def dom_guest():
    if request.cookies.get("role") != "guest":
        resp = make_response(redirect(url_for("dom_guest")))
        resp.set_cookie("role", "guest", httponly=True, samesite="Lax")
        return resp
    return redirect('/dashboard')


# @app.route("/transfer", methods=["GET", "POST"])
# def transfer():
#     if request.method == "POST":
#         to = request.form.get("to")
#         amount = request.form.get("amount")
#         # ... логика перевода
#     return render_template("transfer.html")


def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def validate_csrf_token(token):
    return token and token == session.get("_csrf_token")


@app.route("/transfer", methods=["POST", "GET"])
def transfer():
    token = request.form.get("_csrf_token")
    expected = session.get("_csrf_token")

    if not token or token != expected:
        return render_template("transfer.html", status="неуспешно: неверный CSRF токен")

    to = request.form.get("to")
    amount = request.form.get("amount")
    # ... логика перевода

    return render_template("transfer.html", status="успешно")


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie("role", "", expires=0)
    resp.set_cookie("session", "", expires=0)
    resp.delete_cookie("role")
    return resp


if __name__ == "__main__":
    app.run(debug=False, host='127.0.0.1', port=5000)
