# Image 2 - users API + GET /get_users (names) on port 3000
# Build: docker image build -t zhs13/lab8-zeina_sleiman:0.0.2-RELEASE .
# Run:   docker run -p 3000:3000 -d --name lab8_v2 zhs13/lab8-zeina_sleiman:0.0.2-RELEASE

# start from an official, small Python base image
FROM python:3.12-slim

# copy the requirements file into the image first, so Docker can cache the
# pip install layer and skip it when only app.py changes
COPY ./requirements.txt /app/requirements.txt

# switch working directory (all following commands run inside /app)
WORKDIR /app

# install the dependencies listed in requirements.txt into the image
RUN pip install --no-cache-dir -r requirements.txt

# copy every file from the build context (this folder) into /app
COPY . /app

# port the Flask app listens on inside the container
ENV PORT=3000
EXPOSE 3000

# command executed when a container is started from this image
CMD ["python3", "app.py"]
