-- CreateEnum
CREATE TYPE "TaskStatus" AS ENUM ('QUEUING', 'QUEUED', 'PROCESSING', 'FAILED', 'SUCCEEDED');

-- CreateEnum
CREATE TYPE "CallAttemptStatus" AS ENUM ('CREATED', 'DIALING', 'RINGING', 'CONNECTED', 'COMPLETED', 'NO_ANSWER', 'BUSY', 'REJECTED', 'FAILED');

-- CreateTable
CREATE TABLE "Task" (
    "id" TEXT NOT NULL,
    "userPhone" TEXT NOT NULL,
    "userName" TEXT,
    "recipientPhone" TEXT NOT NULL,
    "recipientName" TEXT,
    "instruction" TEXT NOT NULL,
    "userData" JSONB,
    "status" "TaskStatus" NOT NULL DEFAULT 'QUEUING',
    "result" JSONB,
    "failureReason" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "startedAt" TIMESTAMP(3),
    "completedAt" TIMESTAMP(3),
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Task_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CallAttempt" (
    "id" TEXT NOT NULL,
    "taskId" TEXT NOT NULL,
    "attemptNumber" INTEGER NOT NULL DEFAULT 1,
    "status" "CallAttemptStatus" NOT NULL DEFAULT 'CREATED',
    "providerCallId" TEXT,
    "provider" TEXT,
    "startedAt" TIMESTAMP(3),
    "answeredAt" TIMESTAMP(3),
    "endedAt" TIMESTAMP(3),
    "duration" INTEGER,
    "failureReason" TEXT,
    "transcript" TEXT,
    "recordingUrl" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "CallAttempt_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "CallAttempt_taskId_idx" ON "CallAttempt"("taskId");

-- AddForeignKey
ALTER TABLE "CallAttempt" ADD CONSTRAINT "CallAttempt_taskId_fkey" FOREIGN KEY ("taskId") REFERENCES "Task"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
