# SmartAttend

SmartAttend is a smart attendance management system I built to make the traditional attendance process simpler and more automated.

It has separate interfaces for teachers and students, and uses AI-based face and voice recognition to mark attendance. It uses Supabase for authentication and to store all the application data.

The app is built with Python and Streamlit, and the code is split into separate parts for the UI, database, and AI pipelines.

## Features

**Teacher**
- Create and manage subjects
- Enroll students
- Add student photos for face attendance
- Auto-enroll students
- Share subjects with students
- Take attendance using face recognition
- Take attendance using voice recognition
- View attendance results
- Manage attendance records

**Student**
- Create an account and log in
- View enrolled subjects
- Check attendance records
- Access subject information
- Participate in automated attendance

## AI Attendance

### Face Recognition

The face attendance system uses a student's registered photo to recognize them and mark their attendance automatically.

```
Student Photo -> Face Processing -> Face Recognition -> Student Identification -> Attendance Marked
```

### Voice Recognition

SmartAttend also has a voice-based attendance system. Students give their attendance through voice, and the pipeline processes it to identify the student and record their attendance.

```
Student Voice -> Voice Processing -> Voice Recognition -> Student Identification -> Attendance Marked
```

## Project Structure

```
SmartAttend/
|
├── app.py
|
├── assets/
│   └── smartattend_logo.png
|
├── src/
│   ├── components/
│   │   ├── dialog_add_photo.py
│   │   ├── dialog_attendance_results.py
│   │   ├── dialog_auto_enroll.py
│   │   ├── dialog_create_subject.py
│   │   ├── dialog_enroll.py
│   │   ├── dialog_share_subject.py
│   │   ├── dialog_voice_attendance.py
│   │   ├── footer.py
│   │   ├── header.py
│   │   └── subject_card.py
│   │
│   ├── database/
│   │   ├── config.py
│   │   └── db.py
│   │
│   └── pipelines/
│       ├── face_pipeline.py
│       └── voice_pipeline.py
|
├── .streamlit/
|
├── requirements.txt
├── .gitignore
└── README.md
```

## Tech Stack

- Python - main programming language
- Streamlit - web app and UI
- Supabase - authentication and database
- OpenCV - computer vision and image processing
- NumPy - numerical operations
- Pandas - data handling
- Face Recognition - face-based attendance
- Voice Recognition - voice-based attendance

## Running the Project Locally

1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/SmartAttend.git
cd SmartAttend
```

2. Create a virtual environment

```bash
python -m venv venv
```

3. Activate the environment

On Windows:
```bash
venv\Scripts\activate
```

On Mac/Linux:
```bash
source venv/bin/activate
```

4. Install the dependencies

```bash
pip install -r requirements.txt
```

5. Add Supabase credentials

Create this file locally:

```
.streamlit/secrets.toml
```

Add your Supabase credentials in it:

```toml
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
```

Do not upload secrets.toml to GitHub, it's already excluded through .gitignore.

6. Run SmartAttend

```bash
streamlit run app.py
```

## Deployment

SmartAttend can be deployed using Streamlit Community Cloud. The flow looks like this:

```
Local Development -> GitHub -> Streamlit Community Cloud -> Live Application -> Supabase
```

The deployed app uses the same Supabase project for authentication and storing attendance data.

## Security

Sensitive credentials like Supabase keys are not stored in the source code directly. They're loaded using Streamlit Secrets:

```python
st.secrets["SUPABASE_URL"]
st.secrets["SUPABASE_KEY"]
```

The local secrets.toml file is excluded from Git using .gitignore.

## Future Improvements

- Better face recognition accuracy
- Improved voice recognition
- Attendance analytics and charts
- Attendance report export
- Better authentication and user roles
- Cloud storage improvements
- More scalable database architecture
- Mobile-friendly UI
- More AI-powered attendance insights

## Why I Built This

The main idea behind SmartAttend was to explore how AI can be used to solve a common real-world problem. Instead of manually taking attendance, the goal was to make the process faster and more convenient while keeping records organized digitally.

This project also gave me hands-on experience with Streamlit, Supabase, databases, computer vision, voice processing, and building a complete application from development to deployment.

## Author

Yogya Kumar
Computer Science & Engineering Student

## Feedback

If you find this project interesting, feel free to explore the code and try it out.
