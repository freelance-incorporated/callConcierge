import dotenv from 'dotenv';
import Joi from 'joi';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

dotenv.config({ path: path.join(__dirname, '../../.env') });

const envSchema = Joi.object().keys({
  NODE_ENV: Joi.string()
    .valid('development', 'production', 'test') // Use lowercase standard conventions
    .default('development'),
  PORT: Joi.number().default(3000),
  DB_URL: Joi.string().required().description('PostgreSQL connection URL'),
  REDIS_URL: Joi.string()
    .default('redis://localhost:6379')
    .description('Redis connection URL'),
  WEBHOOK_SECRET: Joi.string().required(),
}).unknown();

const { value: envVars, error } = envSchema
  .prefs({ errors: { label: 'key' } })
  .validate(process.env);

if (error) {
  throw new Error(`Config validation error: ${error.message}`);
}

const config = {
  env: envVars.NODE_ENV,
  port: envVars.PORT,
  db: {
    url: envVars.DB_URL,
  },
  redis: {
    url: envVars.REDIS_URL,
  },
  webhookSecret: envVars.WEBHOOK_SECRET,
};

export default config;