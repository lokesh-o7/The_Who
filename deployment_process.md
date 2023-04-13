# Deployment :

Making a local software programme or service, accessible to public is referred to as deployment. 

Deployment, which verifies that whether the programme is operating successfully in its intended environment, is a crucial step. Once the programme or service is online, it entails installation, setup, testing, and maintenance.

Deployment also makes sure that the programme is working properly. Additionally, it enables the programme to be updated and modified, which is essential because software must develop over time to suit the changing demands of users.

In conclusion, deployment is a crucial step in the software development lifecycle. It lets software developers to effectively deploy new features and updates, ensuring that the product is useful and relevant for its users.






## Here's a step-by-step process on how we deployed a Python application with Heroku:

1.  Create a Heroku account : If you don't have one, create a "Heroku" account by visiting the Heroku website and clicking on the "Sign up for free" button.

2.  Install the Heroku CLI : To deploy your Python application to Heroku, you will need to install the "Heroku CLI". You can do this by visiting the Heroku CLI website and following the installation instructions for your operating system.

3.  Create a new Heroku app : A new application is created in heroku website by clicking "create new" and give a name to it.

4.  Create a `requirements.txt` file : Heroku uses the `requirements.txt` file to know which dependencies your Python application requires. Make sure to create this file in the root directory of your project and list all the dependencies your application needs, one per line.

5.  Create a `Procfile` : The `Procfile` tells Heroku which command to run to start your application. Create a file named `Procfile` in the root directory of your project and add the following line:
    
                 >> worker: python <your-app-name>.py <<

    Make sure to replace `<your-app-name>.py` with the name of the Python file that contains your application code.

6.  Install Git : To push the code to deploy, we need git software to be installed in our computer.

7.  Initialize a Git repository : Initialize a Git repository in the root directory of your project by running the following command:

                <----> git init

8.  Add your files to the Git repository : Add all the files in the root directory of your project to the Git repository by running the following command:

                <----> git add .

9.  Commit your changes : Commit your changes to the Git repository by running the following command:

                <----> git commit -m "Initial commit"

10.  Deploy your application to Heroku : Finally, deploy your application to Heroku by running the following command:

                <----> git push heroku master

Heroku will now build your application and deploy it. That's it! You have successfully deployed your Python application to Heroku.
