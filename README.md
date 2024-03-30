1) Installation

   git clone https://github.com/LAKSHMANA-VINAY/event_management.git

2) Navigate to the project directory:

   cd event_management_directory 

3) Install dependencies using pip:

   pip install Flask
   pip install Flask-SQLAlchemy
   pip install aiohttp

4) Database Setup:

  Ensure you have XAMPP installed and running locally.
  Create a MySQL database for your application.
  Update the SQLALCHEMY_DATABASE_URI in your Flask application's configuration to point to your MySQL database and make database name with event_database.

5) External APIs:
   
  As application relies on external APIs, ensure to keep API keys or tokens required for authentication. Update your application code with these keys or tokens as necessary on lines 35,48,104,117 in app.py.

6) Run the Application:

  Start the Flask development server:
  python app.py
  Your application should now be running locally. Access it in your web browser at http://localhost:5000.

7) Usage:

  Once the application is running, users can access it using the provided URL.
  Provide any necessary instructions for users to interact with your application, such as filling out forms,or accessing specific endpoints.
  Intially to add data in the database make call of http://localhost:5000/events/add.
  And first at line 66 you have to keep the file path of the .csv file.

8) Working Demo: https://drive.google.com/file/d/1N_RvpX6fka7vUajr9l4WVR_ZZrQJ7zG5/view?usp=sharing
  
   
