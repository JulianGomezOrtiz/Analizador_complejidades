from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.server.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_insertion_sort():
    code = """
    PROCEDURE InsertionSort(A, n)
    BEGIN
      FOR i <- 2 TO n DO
      BEGIN
        key <- A[i];
        j <- i - 1;
        WHILE j > 0 and A[j] > key DO
        BEGIN
          A[j+1] <- A[j];
          j <- j - 1;
        END
        A[j+1] <- key;
      END
    END
    """
    response = client.post("/analyze", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    assert "complexity" in data
    assert "n**2" in data["complexity"]["big_theta"]
