def test_root_redirects_to_static_index(client):
    # Arrange
    follow_redirects = False

    # Act
    response = client.get("/", follow_redirects=follow_redirects)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert expected_activity in activities
    assert set(activities[expected_activity]) == {
        "description",
        "schedule",
        "max_participants",
        "participants",
    }
    assert activities[expected_activity]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant_to_activity(client):
    # Arrange
    activity = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in client.get("/activities").json()[activity]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert client.get("/activities").json()[activity]["participants"].count(email) == 1


def test_signup_requires_email(client):
    # Arrange
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_missing_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_requires_email(client):
    # Arrange
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup")

    # Assert
    assert response.status_code == 422


def test_signup_then_unregister_updates_activity_state(client):
    # Arrange
    activity = "Soccer Team"
    email = "new.player@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )
    after_signup = client.get("/activities").json()[activity]["participants"]
    unregister_response = client.delete(
        f"/activities/{activity}/signup", params={"email": email}
    )
    after_unregister = client.get("/activities").json()[activity]["participants"]

    # Assert
    assert signup_response.status_code == 200
    assert email in after_signup
    assert unregister_response.status_code == 200
    assert email not in after_unregister