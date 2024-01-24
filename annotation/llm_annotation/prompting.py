vhc_representation = ('0:{name: Auv1, objectives: [launch, survey, recovery], ready_plan: True, current_obj: "Survey",'
                      ' progress_type: 2, replanning: True, obstacle_found: True, behaviour: Transit}')

agent_description = ("The autonomous agent has a predefined name and a set objectives that it needs to complete "
                     "during a mission. Each objective can either be: launch, survey, target or recovery. The "
                     "behaviours that the agent can exhibit are: Hold Position, Survey, Transit and Wait. The agent "
                     "also has three boolean states (ready_plan, replanning, obstacle_found) and two categorical ("
                     "current_objective, progress_type). If ready_plan is equal to False, then the vehicle is waiting."
                     "If the current_objective is equal to None, then the vehicle is also waiting. If progress type is "
                     "equal to idle, then the agent is waiting, if it's moving towards objective, then the vehicle is "
                     "in transit and if it's performing task then, then the vehicle is doing a Survey.")

task_description = ('\n----------------\n'
                    'You are asked to come up '
                    
                    'You are asked to come up with a set of 5 diverse task instructions in the field of medicine and healthcare.'
                    'All the task instructions have to be based on the context provided above, and cannot require external knowledge or information.'
                    'These tasks will be used to quiz an AI Assistant on the knowledge of the topic above.')

requirements = ('Here are the requirements: \n 1. Try not to repeat the verb for each instruction to maximize diversity.\n'
               '2. The language used for the instruction also should be diverse. For example, you should combine questions with imperative instructions.) \n'
               '3. The type of instructions should be diverse. Create instructions that include diverse kinds of tasks'
               ' like step-by-step reasoning, multiple-choice-questions, open-ended generation, classification, editing,'
               ' complex medical questions, etc.\n'
               '4. Every instruction has to be self-contained, all the information necessary to solve the task has to '
               'be part of the instruction. For example, the instructions should never say "From the provided context" '
               'or "given the context" or "based on the context" or "based on the information".')

task = 'List of 5 task instruction (every task has the following fields: Task Number:, Instruction:, Solution:):'