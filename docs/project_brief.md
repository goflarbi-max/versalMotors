Project Overview
Your task is to design, build, test, and deploy an AI-Powered Automotive Business Intelligence & Decision System.

You are working with an automobile company that sells vehicles and manages activities such as inventory, servicing, warranty claims, customer complaints, and branch operations.
The company collects a lot of information.
However, having data does not automatically mean the company understands what is happening inside the business.
Management wants better answers.
They want to know:
What is happening?
Where are the problems?
Where are the opportunities?
What is changing?
What deserves attention?
What evidence supports these findings?
What actions should be considered?
Your job is to build a system that helps answer these questions.
This is not simply a dashboard project.
This is not simply a chatbot project.
This is not an assignment where you will be told exactly which charts to create.
You are expected to investigate the business problem, work with the available data, decide what matters, and build a useful system around it.

1. The Business Situation
Imagine that senior management approaches you with the following problem:
"We have information across sales, vehicles, branches, inventory, servicing, warranty claims, and customer feedback. We believe there are problems and opportunities hidden inside this information, but we do not have a clear picture of what deserves our attention.
Build us a system that helps us understand the business, investigate important issues, and make better decisions."
That is your assignment.
Management has not told you exactly what the answer is.
You must investigate.

2. Your Mission
Build an AI-powered system that transforms automobile business data into useful business intelligence.
The system should help a decision-maker move through four stages:
UNDERSTAND → INVESTIGATE → EXPLAIN → ACT
Understand
What is happening across the business?
Investigate
Where are unusual patterns, problems, or opportunities?
Explain
What evidence helps explain what is happening?
Act
What actions should management consider?
Your application should support this process.
How you accomplish it is part of the assignment.

3. The Data
Your system should work with realistic automobile-company data.
Your dataset should contain enough information to make analysis meaningful.
At minimum, work with several of the following areas:
Vehicle sales
Vehicle models
Vehicle brands
Branches or locations
Salespeople
Inventory
Vehicle acquisition cost
Selling price
Discounts
Service records
Repair costs
Warranty claims
Customer complaints
Customer satisfaction
Dates and time periods
You may include additional information if it improves your analysis.
Your dataset should contain enough records to reveal patterns.
Do not create a dataset containing only 20 perfectly organised rows.
The system should demonstrate why software and AI become useful when the amount of information becomes difficult to inspect manually.

4. Your First Responsibility: Understand the Business
Do not immediately start building charts.
First, understand the information you have.
Ask questions such as:
What does each dataset represent?
What does each field mean?
How are different datasets connected?
Are there missing values?
Are there duplicate records?
Are there strange values?
Are dates stored correctly?
Are financial values consistent?
Are vehicle names written consistently?
Are some records incomplete?
What information can and cannot be concluded from the data?
Document important assumptions.
A system built on misunderstood data can produce convincing but incorrect conclusions.

5. Data Preparation
Real business data is rarely perfect.
Your system should be able to deal appropriately with problems such as:
Missing values.
Duplicate records.
Incorrect formats.
Inconsistent vehicle names.
Inconsistent branch names.
Unexpected values.
Invalid dates.
Missing relationships between records.
Do not silently change questionable information.
Important cleaning decisions should be explainable.

6. Business Overview
Your system should provide management with a useful overview of the business.
You decide which information deserves to appear.
Possible areas include:
Sales performance.
Revenue.
Profit or margin.
Inventory.
Vehicle performance.
Branch performance.
Service activity.
Warranty activity.
Customer complaints.
Customer satisfaction.
Changes over time.
You are not required to include every possible metric.
Choosing what matters is part of the assignment.
Every number displayed should have a purpose.

7. Investigation
The system must allow the user to move beyond the overview and investigate the business.
For example, a user may want to investigate:
A particular vehicle model.
A branch.
A time period.
A category of customer complaints.
Inventory performance.
Warranty activity.
Sales performance.
Service costs.
The system should make it possible to move from:
"Something looks unusual."
to:
"Let me investigate why."
This is one of the most important parts of the project.

8. Finding What Management Did Not Ask For
Your system should attempt to surface important patterns without requiring management to already know what to search for.
For example, the data might reveal:
A vehicle model with increasing warranty claims.
Inventory that remains unsold for unusually long periods.
A branch with strong revenue but weak margins.
Increasing customer complaints.
A model that sells well in one location but poorly in another.
Unusually high discounting.
Repair costs increasing over time.
Certain complaints repeatedly appearing together.
Customer satisfaction falling while sales remain strong.
A relationship between warranty claims and a particular model or period.
These are examples only.
Do not build the system specifically to reproduce this list.
Your job is to discover what the data actually supports.

9. AI-Powered Business Analysis
Your system must contain a meaningful AI capability.
Adding a chatbot that has no connection to the business data is not enough.
The AI should help users understand or investigate the business.
For example, a user might ask:
"Which vehicle models deserve management attention?"
"What changed in sales during the last three months?"
"Which branches are experiencing unusual warranty activity?"
"Are there patterns in customer complaints?"
"Which vehicles appear to be sitting in inventory for too long?"
"What are the most important things management should know this month?"
The AI should use the available business data when answering.
It should not simply produce generic automobile-industry advice.
10. Evidence Before Claims
This requirement is critical.
If the system makes a claim, the user should be able to understand the evidence behind it.
Suppose the AI says:
"Model X requires attention because warranty activity has increased."
The system should support that statement with relevant data.
For example:
Number of claims.
Change over time.
Relevant branch.
Relevant model.
Comparison period.
Cost impact.
Do not build an application where AI can confidently invent business facts.
The data is the evidence.
AI helps interpret it.

11. Separate Facts From Interpretation
Your system should distinguish between:
Fact
Something directly supported by the data.
Example:
"Warranty claims for Model A increased from 42 to 71."
Interpretation
An explanation or possible meaning.
Example:
"The increase may indicate a reliability issue that deserves investigation."
Recommendation
A possible action.
Example:
"Management should review the warranty cases to determine whether a common component is involved."
These are different.
Your application should not present assumptions as facts.

12. Management Brief
Create a feature that produces a concise Management Brief.
The brief should summarise what management needs to know.
It may include:
Executive Summary
A summary of the current situation.
Key Findings
The most important findings from the data.
Areas Requiring Attention
Problems, unusual patterns, or risks that deserve investigation.
Opportunities
Potential areas where the business could improve performance.
Supporting Evidence
The important numbers or records behind the findings.
Recommended Actions
Actions management should consider.
Questions Requiring Further Investigation
Things the available data cannot fully explain.
The Management Brief should be generated from the actual data available to the system.

13. Ask the Business
Create an AI-powered feature that allows a user to ask questions about the business using normal language.
For example:
"Show me the vehicle models with the highest warranty costs."
"Compare sales performance between branches."
"Which vehicles have been sitting in inventory the longest?"
"What happened to customer complaints this quarter?"
"Give me three things management should investigate."
The system should interpret the question and use the business data to produce an answer.
Where appropriate, show supporting numbers, tables, or visualisations.





14. Filters and Exploration
Users should be able to explore the business without asking AI every time.
Consider useful filters such as:
Date range.
Branch.
Vehicle model.
Brand.
Salesperson.
Status.
Complaint category.
Service category.
The exact filters depend on your data and system design.

15. Visualisations
Use charts where they genuinely improve understanding.
Possible examples include:
Sales over time.
Revenue by branch.
Margin by vehicle model.
Inventory age.
Warranty costs over time.
Complaint trends.
Service activity.
Customer satisfaction.
Do not create charts simply because charts look impressive.
A chart should answer a question.
You should be able to explain:
"This visualization exists because it helps management understand 


16. Drill-Down Capability
A useful business system should allow users to move from a high-level finding to the information underneath it.
For example:
Management Overview
↓
Warranty costs increased
↓
Which models?
↓
Which branches?
↓
Which claims?
The exact implementation is your decision.
The goal is to prevent the system from becoming a collection of numbers with no way to investigate them.

17. Data Quality
Create a section that communicates important data-quality problems.
Examples:
Missing records.
Duplicate records.
Unknown vehicle models.
Missing prices.
Invalid dates.
Missing branch information.
Unusual values.
Management should know when the quality of the underlying information could affect a conclusion.

18. The Unknown Requirement
On Day 4, you will receive an additional business requirement.
You will not know the requirement in advance.
You must integrate it into your existing application.
You should not need to rebuild the entire project.
This is intentional.
Real systems change.
Your project should be structured well enough to accommodate change.

19. Design Requirements
The application should feel appropriate for someone responsible for understanding an automobile business.
It should be:
Clean.
Professional.
Easy to navigate.
Easy to understand.
Responsive.
Fast enough to use comfortably.
It must work properly on:
Mobile phones.
Tablets.
Laptops.
Desktop computers.
Pay particular attention to how tables, charts, filters, and reports behave on smaller screens.

20. Technology
You may choose the technologies you believe are appropriate.
You may use:
AI coding agents.
AI APIs.
Databases.
Data-analysis libraries.
Charting libraries.
Frameworks.
Search tools.
Documentation.
Tutorials.
Online examples.
There is no reward for unnecessary complexity.
Choose technologies because they help you solve the problem.

21. AI Coding Agents
You are strongly encouraged to use AI coding agents throughout the project.
However, your role is changing.
In the previous project, you may have given instructions such as:
"Add a microphone button."
In this project, learn to give instructions based on outcomes.
For example:
"Management needs to identify vehicles that are staying in inventory longer than normal. Examine the current application and propose how we can support that investigation."
Then evaluate what the AI proposes.
Do not accept every AI suggestion automatically.
You are responsible for the final product.

22. GitHub Requirements
Create a public GitHub repository.
Your Git history should demonstrate meaningful development throughout the five days.
Do not wait until the final day to upload everything.
Examples of meaningful commits:
Set up automotive data model
Add data cleaning pipeline
Build management overview
Add branch performance analysis
Add inventory investigation
Connect AI analysis to business data
Add management brief
Add drill-down investigation
Add data quality checks
Improve mobile dashboard
Add Day 4 requirement
Prepare production deployment
Avoid meaningless commits such as:
update
changes
fix
stuff
final
Your GitHub history should tell the story of how the system was built.

23. Five-Day Project Plan
Day 1. Understand the Business and the Data
Do not spend the entire day making the interface beautiful.
Start by understanding the problem.
Complete:
Create the project.
Create the public GitHub repository.
Obtain or create the dataset.
Examine the dataset.
Understand the fields.
Identify relationships between datasets.
Identify data-quality problems.
Decide what questions the system should help answer.
Sketch the system.
Build the basic application structure.
Make meaningful commits.
By the end of Day 1, you should be able to explain:
"This is the information I have, this is what it tells us about the business, and this is how my system will help management use it."

Day 2. Build the Business Intelligence Foundation
Build the core analytical system.
Focus on:
Loading data.
Cleaning data.
Calculating important metrics.
Creating the management overview.
Creating useful filters.
Building initial visualisations.
Creating drill-down capability.
Do not worry about AI yet if the underlying data analysis is not reliable.
AI cannot rescue incorrect numbers.
Commit your progress.
Day 3. Add the Intelligence Layer
Connect AI to the actual business information.
Build capabilities such as
Ask the Business.
Automatic identification of noteworthy patterns.
Management Brief.
Explanation of findings.
Supporting evidence.
Recommended areas for investigation.
Test whether AI answers agree with the underlying data.
Do not assume they will.
Commit your progress.

Day 4. New Requirement and Stress Testing
You will receive the unknown requirement.
Integrate it into the existing application.
Then try to break the system.
Test:
Missing data.
Incorrect values.
Large datasets.
Strange questions.
Questions the data cannot answer.
Different filters.
Mobile layouts.
Failed AI requests.
Contradictory information.
Fix important problems.
Commit your changes.

Day 5. Final Analysis and Deployment
Finish the system.
Then use your own application to analyse the automobile business.
Complete:
Final testing.
README.
Architecture diagram.
Management Brief.
Final business analysis.
GitHub review.
Deployment.
Mobile testing.
Demo video.
Final submission document.
Do not finish the project without using your own system to investigate the business.

24. README Requirements
Your repository must contain a complete README.md.
Include:
Project Name
What is your system called?
Business Problem
What problem are you solving?
Solution
What did you build?
Dataset
What information does the system use?
How the System Works
Explain how data enters the system and becomes useful information.
Architecture
Include a simple architecture diagram.
For example:
Business Data → Data Processing → Database → Analysis → AI Layer → Dashboard → Management
Your architecture may be different.
Technologies
What technologies did you use?
Why?
AI Usage
Where is AI used?
What does AI do?
What does AI not do?
Data Quality
What problems did you discover in the data?
Challenges
Describe at least three meaningful challenges.
AI Mistakes
Describe at least one serious situation where your AI coding agent or AI system produced something wrong or misleading.
Explain how you discovered it.
Explain how you corrected it.
What You Learned
What are the most important things you learned?
Future Improvements
What would you build next?
25. Required Business Investigation
Before submitting, use your system to investigate the company.
Identify at least:
Three Important Findings
What does management need to know?
Two Problems or Risks
What deserves attention?
Two Opportunities
Where might the business improve?
One Surprising Finding
What did you discover that you did not expect?
One Question the Data Cannot Answer
What would require additional information?
Every finding must include supporting evidence.

26. Testing Requirements
Test the system carefully.
At minimum, test:
Different date ranges.
Different branches.
Different vehicle models.
Different business questions.
Missing data.
Incorrect data.
AI questions that can be answered.
AI questions that cannot be answered.
Filters.
Drill-down.
Charts.
Management Brief generation.
Mobile layout.
Desktop layout.
Deployed application.
Also verify important calculations manually.
If your dashboard says:
"Total revenue = X"
You should have some method of verifying that X is correct.
Do not blindly trust AI-generated code to calculate business metrics.

27. Final Demonstration
Record a short demonstration of the finished application.
Your demonstration should tell a story.
Do not simply click every button.
Imagine you are showing the system to management.
Begin with:
"Here is what is happening across the business."
Then demonstrate:
The management overview.
An important finding.
How you investigated that finding.
The evidence underneath it.
Another unexpected pattern.
Ask the Business.
The Management Brief.
Data-quality information.
One question the system cannot confidently answer.
The mobile version.
The viewer should understand why the system is useful.

28. Project Reflection
Answer the following questions in your own words.
Question 1
What did you build?
Question 2
What business problem does it solve?
Question 3
What did you discover about the automobile business from the data?
Question 4
What was the most important finding?
What evidence supports it?
Question 5
What surprised you?
Question 6
Where is AI used in your system?
Question 7
Where did you deliberately choose not to use AI?
Why?
Question 8
What did your AI coding agent get wrong?
Question 9
How did you discover the mistake?
Question 10
What did you do to correct it?
Question 11
What important decision did you make yourself instead of simply accepting the AI's recommendation?
Question 12
What conclusion were you tempted to make but could not support with the available data?
Question 13
What additional data would make your analysis stronger?
Question 14
If 1,000 employees started using your application tomorrow, what would probably break first?
Question 15
If you had another five days, what would you improve?
29. Final Submission
Your final submission must include:
1. Live Application Link
Provide the public link to the deployed system.
2. GitHub Repository Link
Provide the public GitHub repository.
3. Dataset
Provide the dataset used for the project or clearly explain where it came from.
Do not include confidential company information unless you have explicit permission to use and share it.
4. Architecture Diagram
Show the major parts of your system and how information moves between them.
5. Management Brief
Include the final Management Brief produced from your analysis.
6. Business Findings
Provide your:
Three important findings.
Two problems or risks.
Two opportunities.
One surprising finding.
One unanswered question.
Include evidence.
7. Screenshots
Include screenshots showing:
Management overview.
Business investigation.
AI analysis.
Management Brief.
Mobile version.
8. Demo Video
Provide a link to your demonstration.
9. Project Reflection
Answer all required reflection questions.



30. Google Docs Submission
Create a Google Docs document containing your final submission.
The document should be organized professionally and should contain all required links, screenshots, findings, explanations, and reflection answers.
Use the following document title:
Automotive Business Intelligence & Decision System - [Your Full Name]
Your Google Doc should begin with:
Student Name:
[Your Full Name]
Project:
Automotive Business Intelligence & Decision System
Live Application:
[Insert Link]
GitHub Repository:
[Insert Link]
Demo Video:
[Insert Link]
Submission Date:
[Insert Date]
After these details, include the required project materials.

31. Email Submission
When the project is complete, send the final Google Docs submission to:
sekyereasante@gmail.com
Before sending it:
Confirm the Google Doc can be opened.
Check the sharing permissions.
Open the GitHub link yourself.
Open the deployed application yourself.
Open the demo video yourself.
Check that screenshots are visible.
Confirm the architecture diagram is readable.
Confirm your findings contain evidence.
Your submission is not complete if the reviewer cannot access the material.
32. Project Rules
You are allowed and encouraged to use:
AI coding agents.
AI assistants.
Documentation.
Tutorials.
Search engines.
APIs.
Frameworks.
Libraries.
Online examples.
You are not expected to manually write every line of code.
The ability to work effectively with AI tools is part of this project.
However:
You are responsible for the system you submit.
If AI writes code, test it.
If AI produces a calculation, verify it.
If AI makes a business claim, check the evidence.
If AI recommends an architecture, decide whether it makes sense.
If AI produces an error, investigate it.
If AI gives you something you do not understand, ask it to explain it.
You may be asked to explain any major part of your project.
Do not submit something you cannot explain.
33. What Will Be Assessed
Your project will be assessed based on:
Business Understanding
Did you understand the problem before building?
Data Understanding
Can you explain the data and its limitations?
System Design
Did you create a coherent system rather than disconnected features?
Analysis
Does the application help users discover meaningful information?
AI Integration
Is AI being used for a meaningful purpose?
Evidence
Can important claims be supported by data?
Judgment
Can you distinguish facts, interpretations, and recommendations?
User Experience
Can someone understand and use the application?
Reliability
Does the system handle unexpected situations appropriately?
GitHub Usage
Does your repository demonstrate meaningful progress?
Deployment
Does the live application work?
Communication
Can you explain what you built and what you discovered?
Ownership
Can you demonstrate that you understand and can modify the system, even when AI helped you build it?

34. Definition of Done
Your project is considered complete when:
You have a working automobile business dataset.
The data has been examined and prepared.
The application provides a useful management overview.
Users can investigate the business.
Users can filter relevant information.
Users can drill down from findings into supporting information.
The system contains meaningful AI functionality.
Users can ask questions about the business.
AI answers are grounded in available business data.
Important claims contain supporting evidence.
Facts are distinguished from interpretations and recommendations.
The system can produce a Management Brief.
Data-quality problems are communicated.
The application handles questions it cannot answer.
The application works across different screen sizes.
The GitHub repository contains meaningful commits across the project.
The README is complete.
The architecture is documented.
The application is publicly deployed.
The required business investigation has been completed.
The demonstration has been recorded.
The project reflection has been completed.
The final Google Doc has been prepared.
All links have been tested.
The Google Doc has been sent to sekyereasante@gmail.com.
Deadline
5th October, 2026
Final Principle
Your job is not to make the most complicated application possible.
Your job is to take a real business problem, use data and AI intelligently, build something useful, test whether it can be trusted, and communicate what you discovered.
Build something that helps someone make a better decision.
