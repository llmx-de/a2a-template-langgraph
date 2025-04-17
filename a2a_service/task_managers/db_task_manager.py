import logging
from typing import List
from sqlalchemy.orm import Session
from a2a_service.task_managers.async_inmem_task_manager import AgentTaskManager
from a2a_service.database import SessionLocal
from a2a_service.models.db_models import TaskModel, ArtifactModel
from a2a_service.models.task import Task, TaskStatus, Artifact
from a2a_service.models.enums import TaskState


class DatabaseTaskManager(AgentTaskManager):
    """Task manager that persists tasks and artifacts using SQLAlchemy."""

    def __init__(self, agent):
        super().__init__(agent)
        self.logger = logging.getLogger(__name__)

    async def upsert_task(self, task_params):
        """Create or update a task record in the database."""
        db: Session = SessionLocal()
        try:
            db_task = db.get(TaskModel, task_params.id)
            # Extract initial user message if present
            msg_json = None
            if hasattr(task_params, 'message') and task_params.message:
                raw_msg = task_params.message
                if isinstance(raw_msg, dict):
                    msg_json = raw_msg
                else:
                    msg_json = {"role": raw_msg.role, "parts": raw_msg.parts}
            if db_task:
                db_task.session_id = task_params.sessionId
                db_task.state = TaskState.WORKING
                db_task.message = msg_json
            else:
                db_task = TaskModel(
                    id=task_params.id,
                    session_id=task_params.sessionId,
                    state=TaskState.WORKING,
                    message=msg_json
                )
                db.add(db_task)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    async def update_store(self, task_id: str, task_status: TaskStatus, artifacts: List[Artifact] = None) -> Task:
        """Update task status and artifacts in the database and return the updated Task."""
        db: Session = SessionLocal()
        try:
            # Update or insert task record
            db_task = db.get(TaskModel, task_id)

            # Determine message to store: use TaskStatus.message or fallback to latest artifact
            if task_status.message:
                msg_json = {
                    "role": task_status.message.role,
                    "parts": task_status.message.parts
                }
            elif artifacts:
                # Use last artifact as message
                last_art = artifacts[-1]
                msg_json = {
                    "role": "agent",
                    "parts": last_art.parts
                }
            else:
                msg_json = None

            if not db_task:
                db_task = TaskModel(
                    id=task_id,
                    session_id="",
                    state=task_status.state,
                    message=msg_json
                )
                db.add(db_task)
            else:
                db_task.state = task_status.state
                db_task.message = msg_json

            # Insert artifacts
            if artifacts:
                for art in artifacts:
                    db_art = ArtifactModel(
                        task_id=task_id,
                        index=art.index,
                        append=art.append,
                        parts=art.parts
                    )
                    db.add(db_art)

            db.commit()

            # Load all artifacts for this task
            db_artifacts = (
                db.query(ArtifactModel)
                  .filter_by(task_id=task_id)
                  .order_by(ArtifactModel.id)
                  .all()
            )
            # Map to Pydantic artifacts
            py_artifacts: List[Artifact] = [
                Artifact(parts=db_art.parts, index=db_art.index, append=db_art.append)
                for db_art in db_artifacts
            ]

            # Construct TaskStatus
            py_status = TaskStatus(state=db_task.state, message=task_status.message)

            return Task(id=task_id, status=py_status, artifacts=py_artifacts)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close() 