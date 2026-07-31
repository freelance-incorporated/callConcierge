import { Router } from 'express';
import { createTask, getTask } from '../controllers/tasks.controller.js';

const router = Router();

router.post('/', createTask);
router.get('/:id', getTaskById);
router.get('/', getTasks);

export default router;
