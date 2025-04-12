# KEVLAR
Fork of kevlar

## Run the docker image

To execute the software using the provided [Dockerfile](Dockerfile), clone/download the repository and build the image using the command:

```
docker build --build-arg="LANGS=XXX" -t kevlar .
```

where `XXX` is a space-separated list of languages (for instance, `it en`).
The command can be executed without the `--build-arg` parameter. In this case, all the 24 models are downloaded and included (more than 50GB in total).

When the build is complete, run the command:

```
docker run -p 8080:80 kevlar
```

to run with GPU:

```
docker run  --gpus all -e DEVICE=0 -p 8080:80 kevlar
```

where `8080` can be replaced with any other port number, depending of the needs.
In both commands, `kevlar` can be replaced by a custom name.
