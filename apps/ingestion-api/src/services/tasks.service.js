import prisma from "@prisma/client"
import { enqueueTask } from '../queue/tasks.producer.js';

export const createTask = async (data) => {
 const task = await prisma.Task.create({
    data,
 });
 await enqueueTask({
    taskId: task.id,
    ...data
 });
 return task;
}

export const getTaskById = async (id) => {
  return await prisma.Task.findUnique({
    where:{
        id,
    },
  });
}

export const getAllTasks = async () =>{
    return await prisma.Task.findMany({
        orderBy:{
            id:'asc',
        },
    });
}
