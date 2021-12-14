
class Project_helpers:

    def response(self, task):
        if task.goal_id is None:
            return {
                    "id" : task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": self.completed_status(task)
            }
        else:
            return {
                "id" : task.task_id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": self.completed_status(task)
            }


    def not_found(self, task):
        pass

    def completed_status(self, task):
        if task.completed_at is None:
            return False
        return True