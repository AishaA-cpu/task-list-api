from flask import Blueprint, request, jsonify
from flask.helpers import make_response
from app import db
from app.models.goal import Goal
from app.models.task import Task
from datetime import date, datetime
import requests 
from dotenv import load_dotenv
import os

load_dotenv()


task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

# break out request methods into individual functions
# add doct strings into EP definitons

@task_bp.route("", methods=["GET"])
def handle_tasks():
    request_body = request.get_json()
    response_body = []

    tasks = Task.query.all()
    sorting_parameter = request.args.get("sort")

    for task in tasks:
        if task.completed_at is None:
            response_body.append({
                "id" : task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            }) 
        else:
            response_body.append({
                "id" : task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True
            }) 
    if sorting_parameter and sorting_parameter == "asc":
        response_body.sort(key=lambda x:ord(x["title"][0]))
        return jsonify(response_body)

    elif sorting_parameter and sorting_parameter == "desc":
        response_body.sort(reverse=True, key=lambda x:ord(x["title"][0]))
        return jsonify(response_body)

    else:
        return jsonify(response_body)

@task_bp.route("", methods=["POST"])
def add_task():

    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
        return {
            "details": "Invalid data"
        }, 400
    
    else:
        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
        )
        #try:
        db.session.add(new_task)
        db.session.commit()

        if new_task.completed_at is None:
            return {
                "task" : {
                    "id" : new_task.task_id,
                    "title" : new_task.title,
                    "description" : new_task.description,
                    "is_complete" : False
                }
            }, 201
        else:
            return {
                "task" : {
                    "id" : new_task.task_id,
                    "title" : new_task.title,
                    "description" : new_task.description,
                    "is_complete" : True
                }
            }, 201

@task_bp.route("/<task_id>", methods=["GET"])
def get_specific_task(task_id):
    
    task = Task.query.get(task_id)
    if task is None:
        return "", 404

    if task.completed_at is None:
        return {
            "task" : {
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : False
            }
        }, 200
    else:
        return {
            "task" : {
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : True
            }
    }, 200
    # return {
    #     "task" : {
    #         "id" : task.id,
    #         "description" : task.description,
    #         "title": task.title,
    #         "is_complete" : False
    #     },
    # }, 200


@task_bp.route("/<task_id>", methods=["PUT"])
def change_specific_task(task_id):

    task = Task.query.get(task_id)
    if task is None:
        return "", 404
    form_data = request.get_json()

    task.description = form_data["description"]
    task.title = form_data["title"]

    db.session.commit()
    if task.completed_at is None:
        return {
            "task" : {
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : False
            }
        }, 200
    else:
        return {
            "task" : {
                "id" : task.task_id,
                "title" : task.title,
                "description" : task.description,
                "is_complete" : True
            }
        }, 200

@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_specific_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return "", 404

    db.session.delete(task)
    db.session.commit()

    return {
        "details" : f'Task {task.task_id} "{task.title}" successfully deleted'
        }, 200


# *** wave 3 begins ***
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def update_specific_task_complete(task_id):
    request_body = request.get_json()
    
    task = Task.query.get(task_id)

    if task is None:
        return "", 404

    task.completed_at = date.today()
    db.session.commit()
    datas = {
        "channel":"task-notifications",
        "text":f"Someone just completed the task {task.title}"
        
    }
    header = {
        "authorization": os.environ.get("SLACK_ACCESS_TOKEN")
    }
    requests.post('https://slack.com/api/chat.postMessage', params=datas, headers=header)

    return {
        "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True
        }
    }, 200



@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def update_specific_task_incomplete(task_id):
    request_body = request.get_json()
    task = Task.query.get(task_id)

    if task is None:
        return "", 404

    task.completed_at = None
    db.session.commit()

    return {
        "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
        }
    }, 200
    

