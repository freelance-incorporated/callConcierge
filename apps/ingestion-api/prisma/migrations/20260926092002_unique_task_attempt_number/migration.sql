/*
  Warnings:

  - A unique constraint covering the columns `[taskId,attemptNumber]` on the table `CallAttempt` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "CallAttempt_taskId_attemptNumber_key" ON "CallAttempt"("taskId", "attemptNumber");
