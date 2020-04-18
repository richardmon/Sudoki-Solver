"""
Entry point for the web application.

Author: Richard Montoya.
"""
import base64
import json
import os
import uuid
from io import BytesIO
from typing import Optional

from flask import Flask, jsonify, redirect, render_template, request
from PIL import Image
from redis import Redis
from rq import Queue
from rq.job import Job

from images.get_corners import get_corners
from images.transform import transform
from images.presence import get_presence

from images.utils import np_array_to_PIL_image

from models.inference import inference

from Sudoku import solver


URL_REDIS = os.environ.get("URL_REDIS")

if URL_REDIS is None:
    raise ValueError("Environment variable URL_REDIS is not set")

redis_connection = Redis(host=URL_REDIS)
queue = Queue(connection=redis_connection)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/uploader", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        f = request.files["file"]
        uuid_name = str(uuid.uuid4())
        f.save("/tmp/" + uuid_name + ".jpeg")

        job = queue.enqueue(get_corners, "/tmp/" + uuid_name + ".jpeg", result_ttl=-1)
        return render_template("uploader.html", job=job.id)
    return redirect("/", code=302)


@app.route("/job/<job_id>", methods=["GET"])
def get_job(job_id: Optional[str]):
    if not job_id:
        return redirect("/", code=302)
    job = Job.fetch(job_id, connection=redis_connection)
    if job.get_status() != "finished":
        return "loading"
    return jsonify(status="finished")


@app.route("/corners/<job_id>", methods=["GET", "POST"])
def corners(job_id: Optional[str]):
    if not job_id:
        return redirect("/", code=302)
    if request.method == "GET":
        job = Job.fetch(job_id, connection=redis_connection)
        results = job.result
        image_path = results["image"]
        image_shape = results["image_shape"]

        image = Image.open(image_path)
        image = image.resize(tuple(image_shape))
        width, height = image_shape
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return render_template(
            "corners.html",
            corners=json.dumps(results),
            image_str=img_str,
            width=width,
            height=height,
            job_id=job_id,
        )

    elif request.method == "POST":
        old_corners = Job.fetch(job_id, connection=redis_connection)
        corners = request.json
        result = old_corners.result
        # Only preserve the given corners
        corners["image_shape"] = result["image_shape"]
        corners["image"] = result["image"]
        corners["job_id"] = job_id
        job = queue.enqueue(transform, corners, result_ttl=-1)
        url = f"/corners_wait/{job.id}"
        return url


@app.route("/corners_wait/<job_id>", methods=["GET"])
def wait_corner(job_id: str):
    return render_template("corners_wait.html", job=job_id)


@app.route("/transform/<job_id>", methods=["GET", "POST"])
def transform_fetch(job_id: Optional[str]):
    if job_id is None:
        return "NO JOB ID PROVIDED"
    if request.method == "GET":
        image: Image = Job.fetch(job_id, connection=redis_connection).result["image"]
        buffered = BytesIO()

        ## warped
        image_warp: Image = Job.fetch(job_id, connection=redis_connection).result[
            "image"
        ]
        image_warp.save(buffered, format="JPEG")
        ## End warped
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        # buffered.close()
        return render_template("transform.html", image=img_str, job_id=job_id)

    elif request.method == "POST":
        # Get job
        _job = Job.fetch(job_id, connection=redis_connection)
        source_image = _job.result["transform_image"]
        job = queue.enqueue(get_presence, source_image, result_ttl=-1)
        url = f"/transform_wait/{job.id}"
        return url


@app.route("/transform_wait/<job_id>", methods=["GET"])
def transform_wait(job_id: str):
    return render_template("wait_transform.html", job=job_id)


@app.route("/cutting_wait/<job_id>", methods=["GET"])
def cutting_wait(job_id: Optional[str]):
    if not job_id:
        return "NO JOB ID PROVIDED"
    _job = Job.fetch(job_id, connection=redis_connection)
    results = _job.result
    presence_matrix = results["presence"]
    cleared_image = results["cleared"]
    number_image = []
    row, col = presence_matrix.shape
    size = int(306 / 9)
    for i in range(row):
        for j in range(col):
            if presence_matrix[i][j]:
                h = size * j
                w = size * i
                square = cleared_image[
                    size * i : size * (i + 1), size * j : size * (j + 1)
                ]
                number_image.append(square)
    job = queue.enqueue(
        inference, number_image, results["image"], presence_matrix, result_ttl=-1
    )
    return render_template("wait_inference.html", job=job.id)


@app.route("/prediction/<job_id>", methods=["GET", "POST"])
def prediction(job_id):
    if request.method == "GET":
        _job = Job.fetch(job_id, connection=redis_connection)
        results = _job.result
        predictions = results["predictions"]
        image_np = results["original_image"]
        presence = results["presence"]

        image: Image = np_array_to_PIL_image(image_np)
        image = image.resize((360, 360))

        buffered = BytesIO()
        image.save(buffered, format="JPEG")

        width, height = image.size
        inference_array = list(
            map(lambda x: int(x[0][0]) if x[0][1] > 1 else "", predictions)
        )
        image_encoded = base64.b64encode(buffered.getvalue())
        return render_template(
            "predicted_numbers.html",
            inference_array=inference_array,
            image=image_encoded.decode("utf-8"),
            width=width,
            height=height,
            table=presence,
            job_id=job_id,
        )
    elif request.method == "POST":
        data = request.json
        sudoku_int = list(
            map(
                lambda row: list(
                    map(lambda column: int(column) if int(column) else -1, row)
                ),
                data,
            )
        )
        job = queue.enqueue(solver.solve, sudoku_int, result_ttl=-1)
        url = f"/solution_wait/{job.id}"
        return url


@app.route("/solution_wait/<job_id>", methods=["GET"])
def wait_solution(job_id: str):
    return render_template("wait_solution.html", job=job_id)


@app.route("/solution/<job_id>", methods=["GET"])
def solution(job_id: str):
    _job = Job.fetch(job_id, connection=redis_connection)
    results = _job.result
    if results:
        return render_template("solution.html", table=results)
    else:
        return render_template("solution_failed.html")
