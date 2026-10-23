class TaskNotFoundError(Exception):#if the task with given task id is not found in the db
    pass
class TaskNotReadyError(Exception):#if task is still QUEUEING
    pass
class TaskAlreadyFailedError(Exception):# task status is already FAILED
    pass
class TaskUnclaimableError(Exception):#Task status is such that it can't be claimed at the moment
    pass
class TaskExecutionFailedError(Exception):#Task was claimed but the execution couldn't be carried out
    pass
class TaskStateTransitionError(Exception):#SQL executed but for some reason like state mismaatch or task getting deleted somehow it changed 0 rows
    pass
class CallAttemptCreationFailedError(Exception):#If call attempt cant be initiated
    pass
class CallAttemptStateTransitionError(Exception):#If call attempt cstatus cant be changed
    pass