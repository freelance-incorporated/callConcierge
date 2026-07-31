import prisma from "@prisma/client"

export const createTask = async (data) => {
 return await prisma.Task.create({
    data,
 });
}

export const getTaskById = async (id) => {
  return await prisma.Task.findUnique({
    where:{
        id,
    },
  });
}

export const getAllTask = async () =>{
    return await prisma.Task.findMany({
        orderBy:{
            id:'asc',
        },
    });
}


