import * as taskService from '../services/tasks.service.js';

export const createTask = async (req, res, next) => {
  try {
    const data = req.body;
    const result = await taskService.createTask(data);
    if(!result){
      return res.status(400).json({
        message:"Task creation failed!"
      })
    }
    return res.status(200).json({
      message:"Task created successfully"
    });
  } catch (error) {
    next(error);
  }
};

export const getTaskById = async (req, res, next) => {
  try {
    const { id } = req.params;
    const task = await taskService.getTaskById(id);
        if(!task){
      return res.status(400).json({
        message:"Task not found!"
      })
    }
    return res.status(200).json({
      message:"Task fetched successfully",
      task
    });
  } catch (error) {
    next(error);
  }
};

export const getAllTasks = async (req, res, next) => {
  try {
    const tasks = await taskService.getAllTasks();
    if(!tasks){
      return res.status(400).json({
        message:"Task not found!"
      })
    }
    return res.status(200).json({
      message:"Task fetched successfully",
      tasks 
    });
  } catch (error) {
    next(error);
  }
};
