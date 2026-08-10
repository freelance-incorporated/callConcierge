import Joi from 'joi';

const phoneRegex = /^\+?[1-9]\d{1,14}$/;

export const createTaskSchema = Joi.object({
    userPhone: Joi.string()
        .pattern(phoneRegex)
        .message('userPhone must be a valid international phone number (e.g., +1234567890)')
        .required(),
    userName: Joi.string().trim().min(3).max(60).optional(),
    recipientPhone: Joi.string()
        .pattern(phoneRegex)
        .message('recipientPhone must be a valid international phone number (e.g., +1234567890)')
        .required(),
    recipientName: Joi.string().trim().min(3).max(60).optional(),
    instruction: Joi.string().trim().min(5).max(2000).required(),
    userData: Joi.object().optional()
});

export const getTaskByIdSchema = Joi.object({
    id: Joi.string().uuid({ version: 'uuidv4' }).required()
});