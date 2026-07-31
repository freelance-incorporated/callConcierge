import { Router } from 'express';
import { createTask, getTask } from '../controllers/tasks.controller.js';

const router = Router();

router.post('/', createTask);
router.get('/:id', getTask);

export default router;
