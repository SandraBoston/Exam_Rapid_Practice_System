
# PROMPTS AND LESSONS LEARNED FOR AI Code Generation PROCESS IMPROVEMENT: 
# SDLC document revisions:

## SDLC Document Revisions and Tracking IDs:
Documents must be tracked uniquely and versioned. We don't want to overwrite existing documents.  Document revision numbers should have a datestamp suffix and a version number suffix, e.g., 2025-06-16_v1.md  Many revisions may be generated on a specific day and this convention should be sufficient.  At the end of a work period, we will move the older versions to a folder ZZZ_old_versions.

## Scope Reduction:
We need to reduce the scope of the project to only a billing system for water usage.  This is NOT an accounting or bookkeeping system; It is a water usage billing system.  The bills are generated based on the meter readings and the water rates.  The bills are sent to the tenants via email and the payments are received via the tenant's bank account or a check payment.   The bills and payments can be sent to Quicken or QuickBooks Online for record-keeping and tax purposes.

## Project Task durations:
Change these from weeks to hours or 10-minute intervals.  These are small projects done by AI assistants with direction from a human.  They don't need to take longer then a few seconds or minutes.

## Security Simplification:
We need to simplify the security requirements of the project.  We will not be implementing any enterprise security features at this time.  We will only be implementing the most basic security features, such as user authentication and authorization.  We will not be implementing any encryption or secure data storage.


# PROMPT: Capture a complete VERBATIM transcript for today's conversation.  
Write out a complete VERBATIM transcript of today's conversation to a timestamped file before we start the next task.  Make sure to start from the beginning of the conversation, and up to and inclluding this prompt.  Are you clear what to do?   


################ TODO: Action Items: 2025.06.23 ###################

DONE: Rename the folder "Code_Gen_Tracker" to "01_Project_Tracker"


TODO: cleanup entire approach to using conda during Agent-Powered SWE.  
    Ask Copilot how to streamline the process and make it 100% reliable.  

    It needs to be installed before you can use the conda package programmatically.  

    Verify that conda exists in conda environment.yml file.  
    If not, then add conda to the conda environment.yml file.  

I stopped you because the conda package may not be installed in the environment.   

# NEXT STEPS
We added a lot of GREAT functionality and design templates for the front-end GUI.   It looks great now.  

Read the current checklist and project tracker and bring it up to date with the most recent changes. 

# PROMPT: Process Improvement: Leverage the "Lessons Learned" files 
    
    Learn from and Leverage the "Lessons Learned" observations from Task 6 and Task 7.  
    
    Extract the main lessons and turned them into Process Improvement Prompt Library.  

# PROMPT: "Clarify Github Copilot AI Mode Switching"
I just switched from "ASK" mode to "AGENT" mode. Copilot did not force me to start a new conversation. WHY? Usually when I restart VSCode it starts in ASK mode. Then when I switch to AGENT mode, it restarts the conversation completely.

What are the rules for switching between Ask, Edit, and Agent modes with respect to the Chat Conversation Transcript ? Does it matter which LLM model I am using?

Give me a clear ELI5 explanation, and guidance.

