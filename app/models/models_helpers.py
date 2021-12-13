
class Project_helpers:

    def response(self, task):
        if task.completed_at is None:
            return {
                "id" : task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            }
        else:
            return {
                "id" : task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True
            } 

    def not_found(self, task):
        pass