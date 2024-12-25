# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
import flask



initialize_app()


app = flask.Flask(__name__)


@app.get("/")
def hello_world() :
    return "Hello World! FLASK"

#main url for student question bank back end
@https_fn.on_request()
def student_qb_be(req: https_fn.Request) -> https_fn.Response:
     with app.request_context(req.environ):
        return app.full_dispatch_request()