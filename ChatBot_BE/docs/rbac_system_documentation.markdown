# Role-Based Access Control (RBAC) System Documentation

Welcome to the RBAC System Documentation! We're excited to help you navigate our user-friendly platform designed to streamline your workflow based on your role. This document outlines the roles, their permissions, and how you can perform tasks such as creating requests or managing data. Whether you're an Admin, Recruiter, Requestor, or Interviewer, we've got you covered with clear instructions to make your experience seamless and productive.

## What Our Application Does
Our application is a comprehensive **Recruitment Management System** designed to simplify and optimize the hiring process for organizations. It provides a role-based platform that empowers users to manage recruitment tasks efficiently, from creating job requests to sourcing candidates and providing interview feedback. Key features include:
- **Streamlined Request Creation**: Allows authorized users to initiate hiring requests and source candidates through intuitive forms.
- **Role-Based Access Control (RBAC)**: Ensures users only access data and perform actions relevant to their role, enhancing security and efficiency.
- **Data Management**: Enables creation, deletion, updating, and retrieval of recruitment-related data, such as job descriptions, skills, and interview feedback.
- **User-Friendly Dashboards**: Offers tailored dashboards for each role, with dropdown menus and buttons for quick access to tasks.
- **Scalable and Flexible**: Supports various roles (Admin, Recruiter, Requestor, Interviewer) to accommodate organizations of all sizes.

Whether you're managing permissions, posting job descriptions, or evaluating candidates, our application is built to make recruitment smoother, faster, and more organized.

## Overview
The RBAC system assigns permissions to four distinct roles: **Admin**, **Recruiter**, **Requestor**, and **Interviewer**. Each role has access to specific tables in the system and can perform actions such as **Create**, **Delete**, **Update**, and **Retrieve** on those tables. Below, we detail the roles, their accessible tables, and the steps to perform key tasks.

## Roles and Permissions

### 1. Admin
The Admin role has the highest level of access, allowing full control over the system to manage all aspects of recruitment and data.

- **Accessed Tables**:
  - Request Form, Sourcing Form, Report, Skills, Project, Interview Feedback, Job Description, User Permission, Resume Analyzer, Question Bank, Dashboard, Feedback Skills, Designations, Education
- **Permissions**:
  - Create, Delete, Update, and Retrieve data from all listed tables.
- **Functionality**:
  - Upon logging in, Admins are redirected to a dedicated Admin dashboard.
  - The dashboard includes buttons to:
    - Create a **Request Form** (e.g., initiate a new hiring request).
    - Create a **Sourcing Form** (e.g., start sourcing candidates).
  - Admins can access a dropdown menu displaying options: **Designations**, **Feedback Skills**, **Interview Feedback**, **Job Description**, **Project**, **Report**, **Skills**, **User Permission**.
  - By selecting an option from the dropdown, Admins can perform Create, Delete, Update, or Retrieve actions on the corresponding table.

### 2. Recruiter
The Recruiter role focuses on managing recruitment processes, with access to key tables relevant to hiring.

- **Accessed Tables**:
  - Request Form, Sourcing Form, Designations, Education, Feedback Skills, Interview Feedback, Job Description, Project
- **Permissions**:
  - Create, Delete, Update, and Retrieve data from the listed tables.
- **Functionality**:
  - Upon logging in, Recruiters are redirected to a Recruiter dashboard.
  - The dashboard includes buttons to:
    - Create a **Request Form** (e.g., request new hires).
    - Create a **Sourcing Form** (e.g., source candidates).
  - Recruiters can access a dropdown menu displaying options: **Designations**, **Education**, **Feedback Skills**, **Interview Feedback**, **Job Description**, **Project**.
  - By selecting an option from the dropdown, Recruiters can perform Create, Delete, Update, or Retrieve actions on the corresponding table.

### 3. Requestor
The Requestor role is designed for users who initiate requests and manage specific recruitment-related data.

- **Accessed Tables**:
  - Designations, Education, Feedback Skills, Interview Feedback, Job Description
- **Permissions**:
  - Create, Delete, Update, and Retrieve data from the listed tables.
- **Functionality**:
  - Upon logging in, Requestors are redirected to a Requestor dashboard.
  - Requestors can access a dropdown menu displaying options: **Designations**, **Education**, **Feedback Skills**, **Interview Feedback**, **Job Description**.
  - By selecting an option from the dropdown, Requestors can perform Create, Delete, Update, or Retrieve actions on the corresponding table.

### 4. Interviewer
The Interviewer role focuses on providing feedback and managing interview-related data.

- **Accessed Tables**:
  - Designations, Education, Feedback Skills, Interview Feedback, Request Form
- **Permissions**:
  - Create, Delete, Update, and Retrieve data from the listed tables.
- **Functionality**:
  - Upon logging in, Interviewers are redirected to an Interviewer dashboard.
  - Interviewers can access a dropdown menu displaying options: **Designations**, **Education**, **Feedback Skills**, **Interview Feedback**, **Request Form**.
  - By selecting an option from the dropdown, Interviewers can perform Create, Delete, Update, or Retrieve actions on the corresponding table.

## How to Perform Key Tasks
We want to ensure you can easily accomplish your tasks! Below is an example of how to perform a common action: **Creating a Request Form**. This process applies to roles with access to the Request Form table (Admin, Recruiter, Interviewer).

### Creating a Request Form
- **Who Can Create a Request Form?**
  - **Admin**, **Recruiter**, and **Interviewer** roles have permission to create a Request Form.
- **Steps to Create a Request Form**:
  1. **Log in to the System**: Use your credentials (email and password) to access the platform.
  2. **Navigate to Your Dashboard**: Based on your role (Admin, Recruiter, or Interviewer), you’ll be redirected to your respective dashboard.
  3. **Locate the Request Form Option**: Find the **Request Form** button or section on your dashboard (typically marked with a label or icon, such as a "+").
  4. **Initiate a New Request**: Click the "+" button next to the Request Form to open a new form.
  5. **Fill in the Details**: Enter the required information, such as job title, department, or other relevant fields, ensuring all mandatory fields are completed.
  6. **Save the Form**: Review your entries and click the **Save** button at the bottom of the form to submit the request.
- **Result**: The system will save your request, and you’ll receive a confirmation (e.g., a success message or updated request list).

For other actions (e.g., creating a Sourcing Form, updating a Job Description, or deleting Feedback Skills):
- Navigate to the relevant option in your role’s dropdown menu.
- Select the desired action (Create, Delete, Update, Retrieve).
- Follow the on-screen prompts to complete the task, similar to the Request Form process.

## Getting Started
To begin using the system:
1. Log in with your email and password.
2. Explore your role-specific dashboard to familiarize yourself with available actions.
3. Use the dropdown menu or buttons to access tables and perform tasks.
4. If you encounter issues or have questions, our support team is here to assist you!

## Why This System?
Our RBAC system is designed to empower you with the right tools for your role, ensuring efficiency and clarity. Whether you’re managing user permissions as an Admin or providing interview feedback as an Interviewer, we’ve tailored the experience to help you succeed. We’re committed to making your work easier and more impactful!

If you have any questions about performing specific tasks or need further guidance, feel free to reach out. Happy recruiting, and thank you for using our platform!