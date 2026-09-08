import { Router } from 'express';
import { createTask, getAllTasks, getTaskById } from '../controllers/tasks.controller.js';
import { validate } from '../middleware/validate.middleware.js';
import { createTaskSchema, getTaskByIdSchema } from '../schemas/task.schema.js';

const router = Router();

router.post('/', validate(createTaskSchema, 'body'), createTask);
router.get('/:id', validate(getTaskByIdSchema, 'params'), getTaskById);
router.get('/', getAllTasks);

export default router;
