import { Router } from 'express';
import { createCall } from '../controllers/call.controller.js';

const router = Router();

router.post('/', createCall);

export default router;
