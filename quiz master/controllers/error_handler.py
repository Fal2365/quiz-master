from flask import current_app as app, render_template

# Custom error handler for 401 (Page Not Found)
@app.errorhandler(401)
def forbidden(e):
    return render_template('error/401.html'), 403

# Custom error handler for 404 (Page Not Found)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

# Custom error handler for 500 (Internal Server Error)
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500

# Custom error handler for 403 (Forbidden)
@app.errorhandler(403)
def forbidden(e):
    return render_template('error/403.html'), 403

