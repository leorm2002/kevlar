# KEVLAR

KEVLAR (Kessler EuroVoc Laws and Acts Repository) is a set of tools and datasets related to EU laws.
It includes an archive of EU legal documents in 24 languages, covering from 1951 to 2022 and downloaded from EUR-Lex, the software to train a model able to classify documents with respect to the EuroVox taxonomy, a package to run the previous tool as an API, and a web demo.

Authors: Lorenzo Bocchi and Alessio Palmero Aprosio.

Some pre-processing tools are available in different Github projects. In particular, [ScrapeLex](https://github.com/bocchilorenzo/scrapelex) can be used to download and collect legal documents from EUR-Lex, and [AutoEuroVoc](https://github.com/bocchilorenzo/AutoEuroVoc) contains all the code to train and test the models.

The documents can also be downloaded from the KEVLAR [OneDrive repository](https://fbk-my.sharepoint.com/:f:/g/personal/aprosio_fbk_eu/EiHrHFgwhPBKmXQ4Qveaqh0B7eQ98V45ITwvKAdT1mF8CQ?e=XkYXY5). Both the [models](https://dh.fbk.eu/software/kevlar-models/) and the [test data](https://dh.fbk.eu/software/kevlar-test.tar.gz) are available on the Digital Humanities KEVLAR repository.

In this project one can find the [Dockerfile](Dockerfile) that can be used to build an out-of-the-box working environment containing the [classifier (REST API)](src-api), and the [web demo](src-ui).

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

where `8080` can be replaced with any other port number, depending of the needs.
In both commands, `kevlar` can be replaced by a custom name.
