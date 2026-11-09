# Lab 8 – Docker, containers and images

**EECE 435L – Software Tools Lab** · Zeina Sleiman · AUB username `zhs13`

Two images built from the Lab 5 users API:

| Folder | Image | Port | What it adds |
|---|---|---|---|
| `image1-users-api/` | `zhs13/lab8-zeina_sleiman:0.0.1-RELEASE` | 5000 | Lab 5 app as-is |
| `image2-get-users/` | `zhs13/lab8-zeina_sleiman:0.0.2-RELEASE` | 3000 | + `GET /get_users` → JSON list of all user **names** |

(Docker image names must be lowercase, so the name is `lab8-zeina_sleiman`.)

## Build and run (Docker Desktop must be running)

```powershell
cd Lab8\image1-users-api
docker image build -t zhs13/lab8-zeina_sleiman:0.0.1-RELEASE .
docker run -p 5000:5000 -d --name lab8_v1 zhs13/lab8-zeina_sleiman:0.0.1-RELEASE

cd ..\image2-get-users
docker image build -t zhs13/lab8-zeina_sleiman:0.0.2-RELEASE .
docker run -p 3000:3000 -d --name lab8_v2 zhs13/lab8-zeina_sleiman:0.0.2-RELEASE
```

Check in the browser: http://localhost:5000/api/users and http://localhost:3000/get_users

`-p host:container` maps a port on your laptop to the port inside the container. `-d` runs it detached (in the background). The app binds to `0.0.0.0` inside the container, otherwise Flask would only listen on the container's own loopback and the port mapping would not reach it.

## Dockerfile, line by line

- `FROM python:3.12-slim` – base image: Debian with Python preinstalled (the lab uses `python:3.8-alpine`; slim is used here because Python 3.8 is end-of-life and current Flask needs ≥3.9).
- `COPY ./requirements.txt /app/requirements.txt` – copy only the requirements first. Docker caches each instruction as a layer; if `app.py` changes but `requirements.txt` doesn't, the slow `pip install` layer is reused.
- `WORKDIR /app` – directory that all later instructions and the running process use.
- `RUN pip install -r requirements.txt` – executed at **build** time, baked into the image.
- `COPY . /app` – the rest of the code (`.dockerignore` keeps `database.db`, `.venv`, `__pycache__` out).
- `ENV PORT` / `EXPOSE` – `PORT` is read by `app.py`; `EXPOSE` documents which port the container listens on.
- `CMD ["python3", "app.py"]` – executed at **run** time, when a container starts from the image.

## Activity 1 – commands

| Command | What it does |
|---|---|
| `docker ps -a` | Lists **all** containers, running and stopped (`docker ps` alone shows only running ones): container ID, image, status, port mappings, name. |
| `docker stop lab8_v1` | Sends SIGTERM to the container's main process and, after a 10 s grace period, SIGKILL. The container is stopped but not removed – it still shows in `docker ps -a` with status `Exited`. |
| `docker logs lab8_v1` | Prints everything the container's main process wrote to stdout/stderr (here: Flask's startup banner and the request log) – useful for debugging without being attached to it. |

Note: the lab sheet writes `docker stop <image_name>`, but `stop` and `logs` take a **container** name or ID, not an image name – that is why the containers are started with `--name`.

## Submission

- Zip of this `Lab8` folder.
- Activity 1: Word doc with a screenshot after each of the 3 commands + the one-line explanation above.
- Activity 2: Docker Desktop → Images tab screenshot showing both tags.
