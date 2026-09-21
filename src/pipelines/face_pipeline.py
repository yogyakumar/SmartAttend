import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import (
    get_all_students,
    get_student_biometrics
)


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()

    faces = detector(image_np, 1)

    encodings = []

    for face in faces:
        shape = sp(image_np, face)

        face_descriptor = facerec.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        encodings.append(np.array(face_descriptor))

    return encodings


def get_student_training_embeddings(student):
    embeddings = []

    primary = student.get("face_embedding")

    if primary:
        embeddings.append(np.array(primary))

    biometric_rows = get_student_biometrics(
        student["student_id"],
        "face"
    )

    for row in biometric_rows:
        embedding = row.get("embedding")

        if embedding:
            embeddings.append(np.array(embedding))

    return embeddings


@st.cache_resource
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embeddings = get_student_training_embeddings(student)

        for embedding in embeddings:
            X.append(embedding)
            y.append(student.get("student_id"))

    if len(X) == 0:
        return 0

    clf = SVC(
        kernel="linear",
        probability=True,
        class_weight="balanced"
    )

    try:
        clf.fit(X, y)
    except ValueError:
        return 0

    return {
        "clf": clf,
        "X": X,
        "y": y
    }


def train_classifier():
    st.cache_resource.clear()

    model_data = get_trained_model()

    return bool(model_data)


def verify_face_embedding(
    new_embedding,
    stored_embeddings,
    threshold=0.6
):
    if new_embedding is None or not stored_embeddings:
        return False, float("inf")

    new_embedding = np.array(new_embedding)

    best_distance = float("inf")

    for stored in stored_embeddings:
        stored = np.array(stored)

        distance = np.linalg.norm(
            stored - new_embedding
        )

        if distance < best_distance:
            best_distance = distance

    return (
        best_distance <= threshold,
        best_distance
    )


def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)

    X_train = model_data["X"]
    y_train = model_data["y"]

    all_students = sorted(list(set(y_train)))

    if not X_train:
        return detected_student, all_students, len(encodings)

    resemblance_threshold = 0.50

    for encoding in encodings:
        best_distance = float("inf")
        best_student_id = None

        for i, stored_embedding in enumerate(X_train):
            distance = np.linalg.norm(
                np.asarray(stored_embedding) - np.asarray(encoding)
            )

            if distance < best_distance:
                best_distance = distance
                best_student_id = y_train[i]

        if (
            best_student_id is not None
            and best_distance <= resemblance_threshold
        ):
            detected_student[int(best_student_id)] = True

    return (
        detected_student,
        all_students,
        len(encodings)
    )