from flask import Blueprint, request, jsonify
from flask.helpers import make_response
from app import db
from app.models.goal import Goal
from app.models.task import Task
from datetime import date, datetime
from app.models.models_helpers import Project_helpers
import requests 
from dotenv import load_dotenv
from http import HTTPStatus
import os

load_dotenv()


task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

# break out request methods into individual functions
# add doct strings into EP definitons

@task_bp.route("", methods=["GET"])
def handle_tasks():
    """
    route gets all tasks in the database
    if sort argument is provided, sorts according to acs. 
    or desc.
    returns id, title, description of task.
    if no task returns None
    """
    request_body = request.get_json()
    response_body = []
    Response = Project_helpers()
    tasks = Task.query.all()
    sorting_parameter = request.args.get("sort")

    for task in tasks:
        response_body.append(
            Response.response(task)
        )

    # for task in tasks:
    #     if task.completed_at is None:
    #         response_body.append({
    #             "id" : task.task_id,
    #             "title": task.title,
    #             "description": task.description,
    #             "is_complete": False
    #         }) 
    #     else:
    #         response_body.append({
    #             "id" : task.task_id,
    #             "title": task.title,
    #             "description": task.description,
    #             "is_complete": True
    #         }) 
    

    if sorting_parameter and sorting_parameter == "asc":
        response_body.sort(key=lambda x: x["title"])
        return jsonify(response_body)

    elif sorting_parameter and sorting_parameter == "desc":
        response_body.sort(reverse=True, key=lambda x: x["title"])
        return jsonify(response_body)

    else:
        return jsonify(response_body)

@task_bp.route("", methods=["POST"])
def add_task():
    """
    Adds task to data base, returns error is 
    request is missing title, description or completed_at attributes
    returns details of task and created status code
    """
    request_body = request.get_json()
    Response = Project_helpers()
    
    if ("title" not in request_body or "description" not in 
        request_body or "completed_at" not in request_body):
        return {
            "details": "Invalid data"
        }, HTTPStatus.BAD_REQUEST
    
    else:
        new_task = Task(
            title = request_body["title"],
            description = request_body["description"],
            completed_at = request_body["completed_at"]
        )
        #try:
        db.session.add(new_task)
        db.session.commit()

        #if new_task.completed_at is None:
        return {"task": Response.response(new_task)}, HTTPStatus.CREATED
            # return {
            #     "task" : {
            #         "id" : new_task.task_id,
            #         "title" : new_task.title,
            #         "description" : new_task.description,
            #         "is_complete" : False
            #     }
            # }, HTTPStatus.CREATED
        # else:
        #     return {
        #         "task" : {
        #             "id" : new_task.task_id,
        #             "title" : new_task.title,
        #             "description" : new_task.description,
        #             "is_complete" : True
        #         }
        #     }, HTTPStatus.CREATED

@task_bp.route("/<task_id>", methods=["GET"])
def get_specific_task(task_id):
    """
    gets specific task with specified ID if task is not in
    DB, returns None and 404
    success returns details of task
    """
    Response = Project_helpers()

    task = Task.query.get(task_id)
    if task is None:
        return "", HTTPStatus.NOT_FOUND

    return {
        "task" : Response.response(task)
    }, HTTPStatus.OK

    # if task.completed_at is None:
    #     return {
    #         "task" : {
    #             "id" : task.task_id,
    #             "title" : task.title,
    #             "description" : task.description,
    #             "is_complete" : False
    #         }
    #     }, HTTPStatus.OK
    # else:
    #     return {
    #         "task" : {
    #             "id" : task.task_id,
    #             "title" : task.title,
    #             "description" : task.description,
    #             "is_complete" : True
    #         }
    # }, HTTPStatus.OK


@task_bp.route("/<task_id>", methods=["PUT"])
# ***** add code for catching bad request in form 400 code ivalid data****
def change_specific_task(task_id):
    """
    updates task in data base 
    replaces all parts of task in database
    returns None if task is not available and 
    task details if successful
    """
    Response = Project_helpers()

    task = Task.query.get(task_id)
    if task is None:
        return "", HTTPStatus.NOT_FOUND
    form_data = request.get_json()

    task.description = form_data["description"]
    task.title = form_data["title"]
    task.compeleted_at = date.today()

    db.session.commit()

    return {
        "task" : Response.response(task)
    }, HTTPStatus.OK

    # if task.completed_at is None:
    #     return {
    #         "task" : {
    #             "id" : task.task_id,
    #             "title" : task.title,
    #             "description" : task.description,
    #             "is_complete" : False
    #         }
    #     }, HTTPStatus.OK
    # else:
    #     return {
    #         "task" : {
    #             "id" : task.task_id,
    #             "title" : task.title,
    #             "description" : task.description,
    #             "is_complete" : True
    #         }
    #     }, HTTPStatus.OK

@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_specific_task(task_id):
    """
    deletes specific task in database
    """
    task = Task.query.get(task_id)
    if task is None:
        return "", HTTPStatus.NOT_FOUND

    db.session.delete(task)
    db.session.commit()

    return {
        "details" : f'Task {task.task_id} "{task.title}" successfully deleted'
        }, HTTPStatus.OK


# *** wave 3 begins ***
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def update_specific_task_complete(task_id):
    """
    marks specific task as complete
    if task not available returns None
    updates date of compeletion
    posts notification to slack with bot
    returns details of task in and code
    """
    Response = Project_helpers()
    request_body = request.get_json()
    
    task = Task.query.get(task_id)

    if task is None:
        return "", HTTPStatus.NOT_FOUND

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
        "task" : Response.response(task)
    }, HTTPStatus.OK

    # return {
    #     "task": {
    #             "id": task.task_id,
    #             "title": task.title,
    #             "description": task.description,
    #             "is_complete": True
    #     }
    # }, HTTPStatus.OK



@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def update_specific_task_incomplete(task_id):
    """
    marks specific task as incomplete
    if task not available returns None
    updates date of compeletion
    posts notification to slack with bot
    returns details of task in and code
    """
    Response = Project_helpers()
    request_body = request.get_json()
    task = Task.query.get(task_id)

    if task is None:
        return "", HTTPStatus.NOT_FOUND

    task.completed_at = None
    db.session.commit()

    return {
        "task" : Response.response(task)
    }, HTTPStatus.OK
    # return {
    #     "task": {
    #             "id": task.task_id,
    #             "title": task.title,
    #             "description": task.description,
    #             "is_complete": False
    #     }
    # }, HTTPStatus.OK
    
# *** wave 5 begins ****
@goal_bp.route("", methods=["GET"])
def get_all_goals():
    #request_body = request.get_json()
    """
    Gets all available goals in Db
    if no goal, returns None
    """
    response_body = []

    goals = Goal.query.all()

    if goals is None:
        return "", HTTPStatus.OK

    for goal in goals:
        response_body.append({
            "id": goal.goal_id,
            "title": goal.title})

    return jsonify(response_body)

@goal_bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    """
    gets specific goal with specified ID if task is not in
    DB, returns NOne and 404
    success returns details of task
    """
    goal = Goal.query.get(goal_id)

    if goal is None:
        return "", HTTPStatus.NOT_FOUND

    return {
        "goal":{
            "id" : goal.goal_id,
            "title": goal.title
        }
    }, HTTPStatus.OK

@goal_bp.route("", methods=["POST"])
def add_goal():
    """
    Adds task to data base, returns error is 
    request is missing title, description or completed_at attributes
    returns details of task and created status code
    """
    
    request_body = request.get_json()

    if request_body is None:
        return {
            "details": "Invalid data",
        }, HTTPStatus.BAD_REQUEST
    
    if "title" not in request_body:
        return {
            "details": "Invalid data"
        }, HTTPStatus.BAD_REQUEST
    
    else:
        new_goal = Goal(
            title = request_body["title"]
        )
        #try:
        db.session.add(new_goal)
        db.session.commit()

        #return f" i am here"
        return {
            "goal" : {
                "id" : new_goal.goal_id,
                "title" : new_goal.title
            }
        }, HTTPStatus.CREATED

@goal_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    """
    Updates goal title required by test, returns updated goal name
    """
    request_body = request.get_json()
    goal = Goal.query.get(goal_id)

    if goal is None:
        return "", HTTPStatus.NOT_FOUND

    if "title" not in request_body:
        return {
            "details": "Invalid data"
        }, HTTPStatus.BAD_REQUEST
        
    goal.title = request_body["title"]
    
    db.session.commit()

    return {
        "goal": {
                "id": goal.goal_id,
                "title": goal.title
        }
    }, HTTPStatus.OK

@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_one_goal(goal_id):
    """
    deletes goal from db
    """
    
    goal = Goal.query.get(goal_id)

    if goal is None:
        return "", HTTPStatus.NOT_FOUND

    db.session.delete(goal)
    db.session.commit()

    return {
        "details" : f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
    }, HTTPStatus.OK

@goal_bp.route("/<goal_id>/tasks", methods=["POST"])
def assign_tasks_to_goal(goal_id):
    """
    assigns exsisting tasks to goals
    """
    request_body = request.get_json()

    task_ids = request_body["task_ids"]
    goal = Goal.query.get(goal_id)
    
    if goal is None:
        return {
            "", HTTPStatus.NOT_FOUND
        }
        

    for id in request_body["task_ids"]:
        goal.tasks.append(Task.query.get(id))

    db.session.commit()

    return {
        # "successfully created"
        "id":  goal.goal_id,
        "task_ids": task_ids
    }, HTTPStatus.OK

@goal_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_specific_goal(goal_id):
    """
    gets tasks associated with goal
    """
    request_body = request.get_json
    Response = Project_helpers()

    goal = Goal.query.get(goal_id)
    if goal is None:
        return "", HTTPStatus.NOT_FOUND

    response = {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": []
        }

    for task in goal.tasks:
        response["tasks"].append(
            Response.response(task)
            # {
            #     "id" : task.task_id,
            #     "goal_id" : goal.goal_id,
            #     "title": task.title,
            #     "description": task.description,
            #     "is_complete": Response.completed_status(task)
            # }
        )
    

    return response, HTTPStatus.OK

