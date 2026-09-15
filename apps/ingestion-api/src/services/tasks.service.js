import prisma from '../config/db.js';
import { enqueueTask } from '../queue/tasks.producer.js';

export const createTask = async (data) => {
  const task = await prisma.task.create({
    data: { ...data, status: 'QUEUING' },
  });
  try {
    await enqueueTask(task);
  } catch (error) {
    await prisma.task.updateMany({
      where: { id: task.id, status: 'QUEUING' },
      data: {
        status: 'FAILED',
        completedAt: new Date(),
        failureReason: 'Queue publication failed',
      },
    });
    throw error;
  }
  await prisma.task.updateMany({
    where: { id: task.id, status: 'QUEUING' },
    data: { status: 'QUEUED' },
  });
  return prisma.task.findUnique({ where: { id: task.id } });
}

export const getTaskById = async (id) => {
  return await prisma.task.findUnique({
    where:{
        id,
    },
  });
}

export const getAllTasks = async () =>{
    return await prisma.task.findMany({
        orderBy:{
            id:'asc',
        },
    });
}
