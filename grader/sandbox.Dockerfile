FROM python:3.12-alpine
# Sandbox image: no extra packages, runs as nobody (set in runner --user).
# Build: docker build -t codekita-sandbox:latest -f grader/sandbox.Dockerfile grader/
