-- AlterTable
ALTER TABLE "CallAttempt" ALTER COLUMN "providerCallId" DROP NOT NULL,
ALTER COLUMN "provider" SET DEFAULT 'Twilio';
