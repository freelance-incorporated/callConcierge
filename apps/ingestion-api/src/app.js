import express from 'express';
import tasksRoutes from './routes/tasks.routes.js';
import healthRoutes from './routes/health.routes.js';
import { errorHandler } from './middleware/error-handler.js';

const app = express(); 

app.use(express.json());

app.use('/health', healthRoutes);
app.use('/tasks', tasksRoutes);

app.use(errorHandler);

export default app;