# Use a lightweight Python image
FROM python:3-slim

# Set the working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the app using uvicorn
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
