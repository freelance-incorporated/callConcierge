import * as taskService from '../services/tasks.service.js';

export const createTask = async (req, res, next) => {
  try {
    const data = req.body;
    const result = await taskService.createTask(data);
    
  } catch (error) {
    next(error);
  }
};

export const getTask = async (req, res, next) => {
  try {
    const { id } = req.params;
    const result = await taskService.getTaskById(id);
    
  } catch (error) {
    next(error);
  }
};
