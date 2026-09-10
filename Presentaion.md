# Group 2 Approach and solution

We first were assigned a problem of handling messy data with a model. But what kind and how to approach this problem the proper way?

---

# How can we apply AI?

When we studied the problem we found out that AI can not be a magical solution that sovles this problem; and we have reasons.
AI is Stochastic, data are Deterministic. AI provide a probability of success (Confidenece, Accuracy, etc..) if we integerated AI to the data the problem will still be the same, but the cleaning would scale from bad input to AI Halucinations. So we had impelement AI Reasonably.

---

# Generic Pipline

To automate the cleaning proccess we had to make a general pipline that takes any structred data files (CSV, Excel) and then output the same format with cleaned data.

that how we started making answers to questions:
- What is clean data?
- How to generalize?
- Where to apply the AI?

---

# Data groups#:

1. Identity: This data is the data where it has the identification info about the user: Name, Email, Phone (+966).
2. Structed/MetaData: This data is a data where it doesnt identficate the person but tells additional info about him: Major, University.
3. Catagorical/MultiSelcet: This data is usually a multi select data such as: Skills, agreement.
4. Free-Form: This data is the free form space where it takes from the user an input of a question like: Why do you want to join.

---

# The pipeline:

1. Contractor: It mapps the values to the code using LLM
2. Normlaization: Clean and handles the valuse and applies the right cleaning for the right type.
3. DeDuplication: Solving the duplication using unsupervised learning.
4. Loads the data: Loads the cleaned data to a cleaned Excel.

