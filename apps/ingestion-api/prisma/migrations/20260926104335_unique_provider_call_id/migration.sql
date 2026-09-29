 /*
  Warnings:

  - A unique constraint covering the columns `[provider,providerCallId]` on the table `CallAttempt` will be added. If there are existing duplicate values, this will fail.
  - Made the column `providerCallId` on table `CallAttempt` required. This step will fail if there are existing NULL values in that column.
  - Made the column `provider` on table `CallAttempt` required. This step will fail if there are existing NULL values in that column.

*/
-- DropIndex
DROP INDEX "CallAttempt_taskId_idx";

-- AlterTable
ALTER TABLE "CallAttempt" ALTER COLUMN "providerCallId" SET NOT NULL,
ALTER COLUMN "provider" SET NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "CallAttempt_provider_providerCallId_key" ON "CallAttempt"("provider", "providerCallId");
