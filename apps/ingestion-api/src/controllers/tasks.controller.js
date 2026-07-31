import * as taskService from '../services/tasks.service.js';

export const createTask = async (req, res, next) => {
  try {
    const data = req.body;
    const result = await taskService.createTask(data);
    if(!result){
      return res.status(400).json({
        message:"Task creation failed!"
      })
      return res.staus(200).json({
        message:"Task created successfully"
      });
    }
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
      
      return res.staus(200).json({
        message:"Task fetched successfully",
        task
      });
    }
  } catch (error) {
    next(error);
  }
};

export const getTask = async (req, res, next) => {
  try {
    const { id } = req.params;
    const tasks = await taskService.getTask();
        if(!tasks){
      return res.status(400).json({
        message:"Task not found!"
      })
      const {id,recipientPhone,recipientName,instruction,status,updatedAt} = result
      return res.staus(200).json({
        message:"Task fetched successfully",
        tasks
      });
    }
  } catch (error) {
    next(error);
  }
};
