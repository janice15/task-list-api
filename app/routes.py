from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, request, make_response, abort
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        abort(make_response({"message": f"task {task_id} invalid"}, 400))
    
    task = Task.query.get(task_id)
    if not task:
        abort(make_response({"message":f"task {task_id} not found"}, 404))
    return task



# POST request to create new task
@tasks_bp.route("", methods=['POST'])
def create_task():
    request_body = request.get_json()   
    try: 
        new_task = Task(title=request_body["title"], description=request_body["description"], completed_at=None)
    except:
        return {"details": "Invalid data"}, 400
    

    db.session.add(new_task)
    db.session.commit()

    return {
        "task": {
        "id": new_task.task_id,
        "title": new_task.title,
        "description": new_task.description,
        "is_complete": False
        }
    }, 201


@tasks_bp.route("", methods=["GET"])
def get_all_tasks():
    sort_tasks = request.args.get('sort')

    if sort_tasks == 'asc':
        tasks = Task.query.order_by(Task.title.asc()).all()
    elif sort_tasks == 'desc':
        tasks = Task.query.order_by(Task.title.desc()).all()
    else:
        tasks = Task.query.all()

    tasks_response = []
    for task in tasks:
        tasks_response.append({
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False

        }), 

    return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods=["GET"])

def get_by_id(task_id):
    task = validate_task(task_id)

    return {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
  }
    }, 200

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task_to_update = validate_task(task_id)

    request_body = request.get_json()
  
    task_to_update.title = request_body["title"]
    task_to_update.description = request_body["description"]
   

    db.session.commit()

    return {
        "task": {
        "id": task_to_update.task_id,
        "title": task_to_update.title,
        "description": task_to_update.description,
        "is_complete": False
        }
    }, 200


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()

    return{
        "details": f"Task {task_id} \"{task.title}\" successfully deleted"
    }, 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_as_complete(task_id):
    task = validate_task(task_id)

    if task.completed_at is not None:
        return {
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": True
            }
    }, 200

    else:
        task.completed_at = datetime.utcnow()

    db.session.commit()

    return {
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": True
            }
    }, 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])

def mark_as_incomplete(task_id):
    task = validate_task(task_id)

    if task.completed_at is None:
        return {
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
            }
    }, 200 

    else:
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